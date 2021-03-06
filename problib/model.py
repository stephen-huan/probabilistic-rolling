import bisect
from functools import lru_cache
from . import prob, rv

ROLLS = -1             # declare $rolls reset
ROLLS_AVAILABLE = True # whether $rolls is allowed
ROLLS_CYCLE = 8        # how often to use $rolls
ROLLS_F = 1/ROLLS_CYCLE

class Model():

    """ Models interactions with the character kakera random variable. """

    def __init__(self, R: int=prob.R, B: int=prob.B,
                 ROLLS_AVAILABLE: bool=ROLLS_AVAILABLE,
                 ROLLS_CYCLE: int=ROLLS_CYCLE) -> None:
        self.R, self.B, self.offset = R, B, R % B
        self.ROLLS_AVAILABLE, self.ROLLS_CYCLE = ROLLS_AVAILABLE, ROLLS_CYCLE
        # precompute list of expected values for each roll
        self.E = [prob.Ef(r, B) for r in range(prob.upper(R, B) + 1)]
        # methods from prob that are rebound to the specific parameters
        self.fz, self.Fz = lambda z: prob.fz(z, B), prob.Fzs[B]
        self.Ef = lambda r: self.E[r] if r < len(self.E) else prob.Ef(r, B)
        self.f = self.__p_k
        if ROLLS_AVAILABLE:
            self.f = self.__rolls_p_k
            # generate cmf of p_k
            self.Fk = prob.prefix_sum(list(map(self.__p_k, prob.X)))
            # the largest value k* such that Fk(k*) triggers the roll cutoff
            self.kp = prob.X[bisect.bisect(self.Fk, ROLLS_F) - 2]
            assert prob.cmf(self.Fk, self.kp) <= ROLLS_F, "valid cutoff"
            self.rolls_left = 0
        self.p_k = prob.K.map(self.f)
        self.reset()

    def reset(self) -> None:
        """ Reset to the inital model, faster than creating a new model. """
        # number of rolls left, list of seen kakera values, best value
        self.r, self.l, self.b = self.R, [], float("-inf")
        self.size = self.offset if self.offset > 0 else self.B
        self.rolls_use = self.ROLLS_AVAILABLE

    def rolls(self) -> None:
        """ Update the model's parameters if it uses $rolls. """
        delta = prob.upper(self.r + 1, self.B) - self.r
        self.r += delta
        self.size += delta
        self.rolls_use = False

    def update(self, k: int) -> int:
        """ Returns an index if something is worth claiming, otherwise None. """
        # new batch, reset seen and b, the max of the samples we've seen
        if len(self.l) == self.size:
            self.l, self.b, self.size = [], -float("inf"), self.B
        # update variables with new information
        self.l.append(k)
        self.b = max(self.b, k)
        self.r -= 1

        # no need to stop early, wait until the batch is complete 
        if self.b > self.Ef(self.r) and len(self.l) == self.size:
            # use $rolls if emitting this bad of a value has probability 1/8
            if self.rolls_use and self.rolls_left > 0 and self.b <= self.kp:
                self.rolls()
                return ROLLS
            return self.l.index(self.b)

    ### Buying and selling price methods

    def Eloss(self, r: int, k: int) -> float:
        """ Expected value if the current batch is continued.
        k is the best value in the current batch. """
        n = r % self.B
        return prob.capped(prob.Z, prob.Fzs[n], prob.evzs[n], k)

    def status_quo(self, r: int, k: int) -> float:
        """ Represents the current value if we don't buy or sell. """
        return max(self.Eloss(r, k), self.Ef(r))

    def __buy(self, r: int, k: int, b: int) -> float:
        """ Finds the price at which we are indifferent to buying b rolls. """
        return max(self.Ef(r + b) - self.status_quo(r, k), 0)

    def buy(self, b: int=None) -> float:
        """ Calls buy for the current parameters of the model. """
        return self.__buy(self.r, self.b, self.B if b is None else b)

    def __sell(self, r: int, k: int) -> float:
        """ Finds the price at which we are indifferent to selling r rolls. """
        return self.status_quo(r, k) - k

    def sell(self) -> float:
        """ Calls sell for the current parameters of the model. """
        return self.__sell(self.r, self.b)

    ### "Introspective" methods, in order to determine information about
    # the model's random variable itself

    def __Z(self, r: int) -> list:
        """ Returns the correct cmf of Z_n, accounting for offset. """
        return prob.Fzs[self.offset if r >= self.R - self.offset else self.B]

    @lru_cache(maxsize=None)
    def F_r(self, r: int) -> float:
        """ Probability of getting to roll r. The cmf of
        the probability of emitting a value at roll r. """
        # since we never claim in the middle of the batch, use Z instead of X  
        p = prob.cmf(self.__Z(r), self.Ef(r)) if r % self.B == 0 else 1
        return 1 if r == self.R else p*self.F_r(r + 1)

    def p_r(self, r: int) -> float:
        """ Probability of emitting a value at roll r, pmf of F_r. """
        return self.F_r(r) - self.F_r(r - 1)

    def __cache_p_k(self) -> None:
        """ Generate cache for p_k """
        # probability that a value is emitted given we're at level r 
        self.poss = [1 - prob.cmf(self.__Z(r), self.Ef(r))
                     for r in range(self.R)]
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
        return self.fz(k)*self.cond[i] + prob.fz(k, self.offset)*self.coff[i]

    ### Modified introspective models with $rolls

    def p_last(self, k: int) -> float:
        """ Probability of emtting the kakera value k on the last layer. """
        return (1 + prob.cmf(self.Fz, self.kp))*self.fz(k) if k > self.kp \
               else prob.fz(k, 2*self.B)

    def __rolls_p_k(self, k: int) -> float:
        """ Probability of emitting the kakera value k. """
        return self.__p_k(k) + self.p_r(1)*(self.p_last(k) - self.fz(k))

class GeneralModel(Model):

    """ Handles multiple $rolls per claim. Not possible with Mudae rules. """

    def __init__(self, R: int=prob.R, B: int=prob.B,
                 ROLLS_AVAILABLE: bool=ROLLS_AVAILABLE,
                 ROLLS_CYCLE: int=ROLLS_CYCLE) -> None:
        super().__init__(R, B, ROLLS_AVAILABLE, ROLLS_CYCLE)
        if ROLLS_AVAILABLE:
            l, r = 0, prob.N
            while l < r:
                m = (l + r + 1)>>1
                f = prob.cmf(self.Fz, prob.X[m])
                if self.p_r(1)*f/(1 - f) <= ROLLS_F:
                    l, r = m, r
                else:
                    l, r = l, m - 1
            self.kp = prob.X[l]

            f = prob.cmf(self.Fz, self.kp)
            assert self.p_r(1)*f/(1 - f) <= ROLLS_F, "valid cutoff"

            pmf = rv.norm([self.fz(k)*(k > self.kp) for k in prob.K])
            self.p_last = rv.RandomVariable(prob.K, pmf)
            self.p_k = prob.K.map(self.f)

    def rolls(self) -> None:
        """ Update the model's parameters if it uses $rolls. """
        delta = prob.upper(self.r + 1, self.B) - self.r
        self.r += delta
        self.size += delta

def rename(X: rv.RandomVariable, name: str) -> str:
    """ Renames the random variable. """
    X.name = name
    return str(X)

def argmax(l: list, f, minimize: bool=False) -> tuple:
    """ Returns the argmax of f on l, x', and its value, f(x'). """
    x = (min if minimize else max)(l, key=f)
    return x, f(x)

if __name__ == "__main__":
    print(prob.K)
    print(f"min: {prob.K[0]}, max: {prob.K[-1]}, range: {prob.K.range()}")
    print(10*"-")
    rvs = map(lambda args: rename(*args),
              ((prob.K.map(prob.fz), f"Z_{prob.B}"),
               (prob.K.map(lambda z: prob.fz(z, prob.R)), f"Z_{prob.R}"),
               (Model(ROLLS_AVAILABLE=False).p_k, "model"),
               (Model().p_k, "rolls model"),
               (GeneralModel().p_k, "general rolls model")
              ))
    print(f"\n{10*'-'}\n".join(rvs))

    ### is at most one roll per claim justified? 
    rv1, rv2, rv3 = [prob.K.map(lambda z: prob.fz(z, i*prob.B))
                     for i in range(1, 4)]
    k1, evdiff = argmax(rv3, lambda k: rv2.capped(k) - rv1.capped(k))
    # equivalent to sum(max(k - k2, 0)*rv1(k) for k in rv1)
    k2, mindiff = argmax(range(prob.K[0], Model().kp + 1),
                         lambda k: rv1.capped(k) - k, minimize=True)
    print(k1, k2)
    print(f" best expected gain from second use of $rolls: {evdiff:.3f}")
    print(f"worst expected gain from  first use of $rolls: {mindiff:.3f}")

