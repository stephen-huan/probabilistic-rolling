import prob
# comparing two scalars, comparing two lists, allowed distance from 1 
EPSILON, LIST_EPS, DIST = 0.1, 0.01, 10**-3

def EV(l: list, domain: list=prob.X) -> float:
    """ Expected value of a pmf represented by a list. """
    return sum(domain[i]*l[i] for i in range(len(domain)))

def apply(f, r: range=prob.X) -> list:
    """ Applies a function to a range. """
    return list(map(f, r))

def norm(l: list, f: float=None) -> list:
    """ Normalizes a list into a pmf by dividing by its sum. """
    s = sum(l) if f is None else f
    return [x/s for x in l]

def norm_cmf(l: list) -> list:
    """ Normalizes a list into a cmf by dividing by its largest value. """
    return norm(l, max(l))

def nonneg(l: list) -> bool:
    """ Whether all the values in a list are positive. """
    return all(map(lambda x: x >= 0, l))

def pmf(l: list, tol: float=DIST) -> bool:
    """ Whether a list can be interpreted as a pmf. """
    return nonneg(l) and diff(sum(l), 1, tol)

def cmf(l: list, tol: float=DIST) -> bool:
    """ Whether a list can be interpreted as a cmf. """
    return nonneg(l) and l == sorted(l) and diff(l[-1], 1, tol)

def diff(x: float, y: float, tol: float=EPSILON) -> bool:
    """ Whether two numbers are sufficiently close. """
    return abs(x - y) < tol

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
        adiff(EV(u, domain), EV(v, domain), s + " expected value")
    f = lambda l: [round(x, 3) for x in l]
    assert all(map(lambda x: diff(x[0], x[1], tol), zip(u, v))), \
        f"{s}:\n{f(u)} !=\n{f(v)}"

def fdiff(u: list, f, domain: list, s: str,
          is_cmf: bool=False, tol: float=LIST_EPS) -> None:
    """ Whether the [p/c]mf represented by u is equal to the function f.
        Assumes u is simulated and f is theoretical. """
    u, v = (norm_cmf if is_cmf else norm)(u), apply(f, domain)
    pdiff(u, v, s, is_cmf, domain, tol)

