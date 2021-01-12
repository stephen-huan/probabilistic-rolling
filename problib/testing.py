from . import prob
from .rv import norm, norm_cmf, pmf, cmf, diff
# comparing two scalars, comparing two lists
EPSILON, LIST_EPS = 0.1, 0.01

def apply(f, r: range=prob.X) -> list:
    """ Applies a function to a range. """
    return list(map(f, r))

def adiff(x: float, y: float, s: str, tol: float=EPSILON) -> None:
    """ Asserts that two numbers are sufficiently close. """
    assert diff(x, y, tol), f"{s}: {x:.3f} != {y:.3f}"

def pdiff(u: list, v: list, s: str, is_cmf: bool=False,
          domain: list=prob.X, tol: float=LIST_EPS) -> None:
    """ Whether each number in u is close enough to each number in v. """
    assert len(u) == len(v), f"{s}: lists are not of the same length"
    if is_cmf:
        assert cmf(u) and cmf(v), f"{s}: list is not a valid cmf"
    else:
        assert pmf(u) and pmf(v), f"{s}: list is not a valid pmf"
        # expected value calculation is better than element-wise comparison
        adiff(prob.E(u, domain), prob.E(v, domain), s + " expected value")
    f = lambda l: [round(x, 3) for x in l]
    assert all(map(lambda x: diff(x[0], x[1], tol), zip(u, v))), \
        f"{s}:\n{f(u)} !=\n{f(v)}"

def fdiff(u: list, f, domain: list, s: str,
          is_cmf: bool=False, tol: float=LIST_EPS) -> None:
    """ Whether the [p/c]mf represented by u is equal to the function f.
        Assumes u is simulated and f is theoretical. """
    u, v = (norm_cmf if is_cmf else norm)(u), apply(f, domain)
    pdiff(u, v, s, is_cmf, domain, tol)

