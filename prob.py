import bisect, sys
from functools import lru_cache
sys.setrecursionlimit(10**4)

### Random variables, pmfs and cmfs, constants, and setup
"""
X is a discrete random variable (r.v.)
p is its corresponding probability mass function (pmf)
E[X] is the expected value of X
"""
X = [   1,    5,  10,   15,   16,   20,  30,   35,   50,  100]
p = [0.05, 0.08, 0.1, 0.12, 0.17, 0.22, 0.1,  0.1, 0.05, 0.01]
assert sum(p) == 1

# number of discrete values, number of rolls, number of rolls per batch
N, R, B = len(X), 30, 10

def prefix_sum(l: list) -> list:
    """ Returns the prefix sum of l """
    prefix = [0]*(len(l) + 1)
    for i in range(len(l)):
        prefix[i + 1] = prefix[i] + l[i]
    return prefix

# prefix sum of probability list, aka the cumulative mass function (cmf)
F = prefix_sum(p)
# expected value prefix sum
ev = prefix_sum([X[i]*p[i] for i in range(N)])
# value to index
D = {x: i for i, x in enumerate(X)}

def f(x: float) -> float:
    """ pmf of X """
    return p[D[x]]

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

def lower(r: int) -> int:
    """ Returns the largest value n such that n <= r and n % B == 0. """
    return r - (r % B)

def upper(r: int) -> int:
    """ Returns the smallest value n such that n >= r and n % B == 0. """
    return r + (-r % B)

### functions

def cmf(F: list, u: float) -> float:
    """ Finds the value of the cmf at a value in/not in the underlying r.v. """
    # use F if u is in the support set, otherwise binary search
    return F[D[u] + 1] if u in D else F[bisect.bisect(X, u)]

def query(prefix: list, i: int, j: int) -> float:
    """ Finds the sum of a list between two indexes. """
    return prefix[j + 1] - prefix[i]

def __capped(X: list, f: "pmf", u: float) -> float:
    """ Returns E[X], but with the values capped at a minimum of u. """
    return sum(max(x, u)*f(x) for x in X)

def capped(X: list, F: "cmf", prefix: list, u: float) -> float:
    """ Returns E[X] in O(log n). """
    i = bisect.bisect(X, u)
    return u*F[i] + query(prefix, i, N - 1)

@lru_cache(maxsize=None)
def E(i: int, r: int) -> float:
    """ E[X_r], where X_r is X with possibly r more samples. """
    # if r = 0, then we're out of samples and has a constant value of 0
    return 0 if r <= 0 else capped(rvs[i], cmfs[i], evs[i], E(i, r - 1))

@lru_cache(maxsize=None)
def Ef(r: int) -> float:
    """ E[X_f], where Z_r is extended to r's that are not multiples of 10. """
    n = r % B if r % B != 0 else B
    return 0 if r <= 0 else capped(Z, Fzs[n], evzs[n], Ef(r - n))

# list of random variables and their corresponding cmfs to index for lru_cache
rvs, cmfs, evs = [X, Z], [F, Fz], [ev, evzs[B]]

# extension 3: buying rolls and extension 4: selling rolls
def price(r: int, k: int) -> float:
    """ The amount of kakera one should pay if they have r rolls and buy k. """
    return Ef(r + k) - Ef(r)

if __name__ == "__main__":
    # basic model, once you sample X you can't "go back" to the value
    print(E(0, 0), E(0, 1), E(0, R))
    # extension 1: batches of 10
    print(E(0, 0), E(0, 10), E(0, 20), E(0, R))
    print(E(1, 0), E(1, 1),  E(1, 2),  E(1, BATCHES))
    # extension 2: fractional batches
    print(Ef(0), Ef(10), Ef(20), Ef(R))
    print(Ef(1), Ef(12), Ef(25), Ef(27))

