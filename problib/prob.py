import bisect, sys, math
from functools import lru_cache
from .data import X, p
sys.setrecursionlimit(10**4)

### Random variables, pmfs and cmfs, constants, and setup
"""
X is a discrete random variable (r.v.)
p is its corresponding probability mass function (pmf)
E[X] is the expected value of X
"""
# X = [   1,    5,  10,   15,   16,   20,  30,   35,   50,  100]
# p = [0.05, 0.08, 0.1, 0.12, 0.17, 0.22, 0.1,  0.1, 0.05, 0.01]
assert sorted(X) == X, "support set must be sorted"
assert abs(sum(p) - 1) < 10**-3, "not a valid pmf"

# number of discrete values, number of rolls, number of rolls per batch
N, R, B = len(X), 30, 10
# value to index
D = {x: i for i, x in enumerate(X)}

def prefix_sum(l: list) -> list:
    """ Returns the prefix sum of l """
    prefix = [0]*(len(l) + 1)
    for i in range(len(l)):
        prefix[i + 1] = prefix[i] + l[i]
    return prefix

def pmf(p: list, u: float) -> float:
    """ Finds the value of the pmf at a value in/not in the underlying r.v. """
    return p[D[u]] if u in D else 0

def cmf(F: list, u: float) -> float:
    """ Finds the value of the cmf at a value in/not in the underlying r.v. """
    # use F if u is in the support set, otherwise binary search
    return F[D[u] + 1] if u in D else F[bisect.bisect(X, u)]

# prefix sum of probability list, aka the cumulative mass function (cmf)
F, f = prefix_sum(p), lambda x: pmf(p, x)
# expected value prefix sum
ev = prefix_sum([X[i]*p[i] for i in range(N)])

# Z is the r.v. corresponding to sampling X b times and taking the max value 
# Z has the same support set as X but a different pmf
Z, BATCHES = list(X), R//B

# cmf of Z is just the power of each term in the cmf of X
Fzs = [[pow(v, b) for v in F] for b in range(B + 1)]
# expected value prefix sum similar to X 
evzs = [prefix_sum([X[i]*(Fzs[b][i + 1] - Fzs[b][i]) for i in range(N)])
        for b in range(len(Fzs))]
Fz = Fzs[B]

@lru_cache(maxsize=None)
def fz(z: float, b: int=B) -> float:
    """ pmf of Z """
    return pow(F[D[z] + 1], b) - pow(F[D[z]], b)

def lower(r: int, b: int=B) -> int:
    """ Returns the largest value n such that n <= r and n % B == 0. """
    return r - (r % b)

def upper(r: int, b: int=B) -> int:
    """ Returns the smallest value n such that n >= r and n % B == 0. """
    return r + (-r % b)

### probability theory functions

def E(p: list, rv: list=X, f=lambda x: x) -> float:
    """ Expected value of a pmf represented by a list. """
    return sum(f(rv[i])*p[i] for i in range(len(rv)))

def Var(p: list, rv: list=X) -> float:
    """ Var[X] = E[(x - u)^2] = E[X^2] - E[x]^2. """
    return E(p, X, lambda x: x*x) - E(p, rv)**2

def std(p: list, rv: list=X) -> float:
    """ sigma^2 = Var[x] so sigma = standard deviation = sqrt(Var[X]). """
    return math.sqrt(Var(p))

### functions

def query(prefix: list, i: int, j: int) -> float:
    """ Finds the sum of a list between two indexes. """
    return prefix[j + 1] - prefix[i]

def __capped(X: list, p: list, u: float) -> float:
    """ Returns E[X], but with the values capped at a minimum of u. """
    return E(p, X, lambda x: max(x, u))

def capped(X: list, F: "cmf", prefix: list, u: float) -> float:
    """ Returns E[X] in O(log n). """
    i = bisect.bisect(X, u)
    return u*F[i] + query(prefix, i, N - 1)

@lru_cache(maxsize=None)
def Er(i: int, r: int) -> float:
    """ E[X_r], where X_r is X with possibly r more samples. """
    # if r = 0, then we're out of samples and has a constant value of 0
    return 0 if r <= 0 else capped(rvs[i], cmfs[i], evs[i], Er(i, r - 1))

@lru_cache(maxsize=None)
def Ef(r: int, b: int=B) -> float:
    """ E[X_f], where Z_r is extended to r's that are not multiples of 10. """
    n = r % b if r % b != 0 else b
    return 0 if r <= 0 else capped(Z, Fzs[n], evzs[n], Ef(r - n, b))

# list of random variables and their corresponding cmfs to index for lru_cache
rvs, cmfs, evs = [X, Z], [F, Fz], [ev, evzs[B]]

# extension 3: buying rolls and extension 4: selling rolls
def price(r: int, k: int, b: int=B) -> float:
    """ The amount of kakera one should pay if they have r rolls and buy k. """
    return Ef(r + k, b) - Ef(r, b)

if __name__ == "__main__":
    # basic model, once you sample X you can't "go back" to the value
    print(Er(0, 0), Er(0, 1), Er(0, R))
    # extension 1: batches of 10
    print(Er(0, 0), Er(0, 10), Er(0, 20), Er(0, R))
    print(Er(1, 0), Er(1, 1),  Er(1, 2),  Er(1, BATCHES))
    # extension 2: fractional batches
    print(Ef(0), Ef(10), Ef(20), Ef(R))
    print(Ef(1), Ef(12), Ef(25), Ef(27))

