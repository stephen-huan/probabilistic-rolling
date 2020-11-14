import bisect
from functools import lru_cache
import prob

ROLLS = -1             # declare $rolls reset
ROLLS_AVAILABLE = False # whether $rolls is allowed
ROLLS_CUTOFF = 1/8     # how often to use $rolls

class Model():

    """ Models interactions with the character kakera random variable. """

    def __init__(self, R: int) -> None:
        # offset if number of rolls is not a multiple of the batch size
        self.R, self.offset = R, R % prob.B
        # precompute list of expected values for each roll
        self.E = list(map(prob.Ef, range(R + 1)))
        self.reset()
        if ROLLS_AVAILABLE:
            # generate cmf of p_k
            self.Fk = prob.prefix_sum(list(map(self.p_k, prob.Z)))

    def reset(self) -> None:
        """ Reset to the inital model, faster than creating a new model. """
        # number of rolls left, list of seen kakera values, best value
        self.r, self.l, self.b = self.R, [], float("-inf")
        self.off = self.R % prob.B
        self.rolls = ROLLS_AVAILABLE

    def update(self, k: int) -> int:
        """ Returns an index if something is worth claiming, otherwise None. """
        # in the case of an offset, remove the offset first
        B = self.off if self.off is not None else prob.B
        # new batch, reset seen and b
        if len(self.l) == B:
            self.l, self.b, self.off, B = [], -float("inf"), None, prob.B
        # update variables with new information
        self.l.append(k)
        self.b = max(self.b, k)
        self.r -= 1

        # no need to stop early, wait until the batch is complete 
        if self.b > self.E[self.r] and len(self.l) == B:
            # use $rolls if emitting this bad of a value has probability 1/8
            if self.rolls and self.Fk[prob.d[self.b] + 1] <= ROLLS_CUTOFF:
                self.r += len(self.l)
                self.rolls = False
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
    def p_k(self, k: int) -> float:
        """ Probability of emitting the kakera value k. """
        # lazily generate cache on demand
        if not hasattr(self, "poss"):
            self.__cache_p_k()
        i = min(bisect.bisect(self.E, k), self.R)
        return prob.fz(k)*self.cond[i] + prob.fz(k, self.offset)*self.coff[i]

