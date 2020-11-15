import bisect
from functools import lru_cache
import prob

ROLLS = -1             # declare $rolls reset
ROLLS_AVAILABLE = False # whether $rolls is allowed
ROLLS_CYCLE = 8        # how often to use $rolls
ROLLS_F = 1/ROLLS_CYCLE

class Model():

    """ Models interactions with the character kakera random variable. """

    def __init__(self, R: int) -> None:
        self.R, self.offset = R, R % prob.B
        # precompute list of expected values for each roll
        self.E = list(map(prob.Ef, range(prob.upper(R) + 1)))
        self.reset()
        self.p_k = self.__p_k
        if ROLLS_AVAILABLE:
            # generate cmf of p_k
            self.Fk = prob.prefix_sum(list(map(self.__p_k, prob.Z)))
            # the largest value k* such that Fk(k*) triggers the roll cutoff
            self.kp = prob.X[bisect.bisect(self.Fk, ROLLS_F) - 2]
            assert prob.cmf(self.Fk, self.kp) <= ROLLS_F, "valid cutoff"
            self.rolls_left = 0

    def reset(self) -> None:
        """ Reset to the inital model, faster than creating a new model. """
        # number of rolls left, list of seen kakera values, best value
        self.r, self.l, self.b = self.R, [], float("-inf")
        self.B = self.offset if self.offset > 0 else prob.B
        self.rolls_use = ROLLS_AVAILABLE

    def update(self, k: int) -> int:
        """ Returns an index if something is worth claiming, otherwise None. """
        # new batch, reset seen and b, the max of the samples we've seen
        if len(self.l) == self.B:
            self.l, self.b, self.B = [], -float("inf"), prob.B
        # update variables with new information
        self.l.append(k)
        self.b = max(self.b, k)
        self.r -= 1

        # no need to stop early, wait until the batch is complete 
        if self.b > self.E[self.r] and len(self.l) == self.B:
            # use $rolls if emitting this bad of a value has probability 1/8
            if self.rolls_use and self.rolls_left > 0 and self.b <= self.kp:
                delta = prob.upper(self.r + 1) - self.r
                self.r += delta
                self.B += delta
                self.rolls_use = False
                return ROLLS

            return self.l.index(self.b)

    ### "Introspective" methods, in order to determine information about
    # the model's random variable itself

    def __Z(self, r: int) -> list:
        """ Returns the correct cmf of Z_n, accounting for offset. """
        return prob.Fzs[self.offset] if r >= self.R - self.offset else prob.Fz

    @lru_cache(maxsize=None)
    def F_r(self, r: int) -> float:
        """ Probability of getting to roll r. The cmf of
        the probability of emitting a value at roll r. """
        # since we never claim in the middle of the batch, use Z instead of X  
        p = prob.cmf(self.__Z(r), self.E[r]) if r % prob.B == 0 else 1
        return 1 if r == self.R else p*self.F_r(r + 1)

    def p_r(self, r: int) -> float:
        """ Probability of emitting a value at roll r, pmf of F_r. """
        return self.F_r(r) - self.F_r(r - 1)

    def __cache_p_k(self) -> None:
        """ Generate cache for p_k """
        # probability that a value is emitted given we're at level r 
        self.poss = [1 - prob.cmf(self.__Z(r), self.E[r]) for r in range(self.R)]
        # prefix sum of the probability we reach level r over its value emission   
        i, f = self.R - self.offset, lambda r: self.p_r(r + 1)/self.poss[r]
        self.cond = prob.prefix_sum(list(map(f, range(i))) + [0]*self.offset)
        self.coff = prob.prefix_sum([0]*i + list(map(f, range(i, self.R))))

    @lru_cache(maxsize=None)
    def __p_k(self, k: int) -> float:
        """ Probability of emitting the kakera value k. """
        # lazily generate cache on demand
        if not hasattr(self, "poss"):
            self.__cache_p_k()
        i = min(bisect.bisect(self.E, k), self.R)
        return prob.fz(k)*self.cond[i] + prob.fz(k, self.offset)*self.coff[i]

    ### modified introspective models with $rolls

    def p_last(self, k: int) -> float:
        """ Probability of emtting the kakera value k on the last layer. """
        return (1 + prob.cmf(prob.Fz, self.kp))*prob.fz(k) if k > self.kp \
               else prob.fz(k, 2*prob.B)

    def rolls_p_k(self, k: int) -> float:
        """ Probability of emitting the kakera value k. """
        return self.__p_k(k) + self.p_r(1)*1

