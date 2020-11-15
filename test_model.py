import random, bisect, sys
import prob, model

random.seed(1)
ITERS, EPSILON, LIST_EPSILON = 10**5, 0.1, 0.01
count_Fr = [0]*(prob.R + 1)
count_pr = [0]*(prob.R + 1)
count_k  = [0]*prob.N
count_rolls = [0]
count_last = [0]*prob.N

def sample(X: list, F: list) -> float:
    """ Samples a value from a random variable. """
    p = random.random()
    return X[bisect.bisect(F, p) - 1]

def simulate(m: model.Model=model.Model(prob.R), index: int=0) -> float:
    """ Simulates a game. """
    m.reset()
    # give the model a roll every ROLLS_CYCLE claim iterations
    if model.ROLLS_AVAILABLE and index % model.ROLLS_CYCLE == 0:
        m.rolls_left += 1
    l = []
    # offset if number of rolls is not a multiple of the batch size
    offset = prob.R % prob.B
    # in the case of an offset, remove the offset first
    size = offset if offset > 0 else prob.B
    r = prob.R
    used = False
    while r > 0:
        if r <= prob.R:
            count_Fr[r] += 1
        # new batch, reset seen and assume offset has been taken care of
        if len(l) == size:
            l, size = [], prob.B
        k = sample(prob.X, prob.F)
        l.append(k)
        # give kakera value to the model 
        i = m.update(k)
        if i is not None:
            if i == model.ROLLS:
                assert model.ROLLS_AVAILABLE, "$rolls is not allowed"
                assert m.rolls_left > 0, "model doesn't have available rolls"
                count_rolls[0] += 1
                # $rolls resets the batch instead of adding the batch size
                delta = prob.upper(r) - r + 1
                r += delta
                size += delta
                m.rolls_left -= 1
            else:
                assert 0 <= i < len(l), "model did not give a valid index"
                count_pr[r] += 1
                count_k[prob.D[l[i]]] += 1
                if r == 1:
                    count_last[prob.D[l[i]]] += 1
                return l[i]
        r -= 1
    # model didn't claim, kakera value of 0
    return 0

def E(X, iters: int=ITERS) -> float:
    """ Expected value by repeatedly sampling a random variable. """
    return sum(X() for i in range(iters))/iters

def apply(f, r: range) -> list:
    """ Applies a function to a range. """
    return list(map(f, r))

def norm(l: list, f: float=None) -> list:
    """ Normalizes a list into a pmf by dividing by its sum. """
    s = sum(l) if f is None else f
    return [x/s for x in l]

def diff(x: float, y: float, tol: float=EPSILON) -> bool:
    """ Whether two numbers are sufficiently close. """
    return abs(x - y) < tol

def adiff(x: float, y: float, s: str, tol: float=EPSILON) -> None:
    """ Asserts that two numbers are sufficiently close. """
    assert diff(x, y, tol), f"{s}: {x:.3f} != {y:.3f}"

def ldiff(u: list, v: list, s: str, tol: float=LIST_EPSILON) -> None:
    """ Whether each number in u is close enough to each number in v. """
    f = lambda l: [round(x, 3) for x in l]
    assert len(u) == len(v), f"{s}: lists are not of the same length"
    assert all(map(lambda x: diff(x[0], x[1], tol), zip(u, v))), \
        f"{s}:\n{f(u)} !=\n{f(v)}"

if __name__ == "__main__":
    m = model.Model(prob.R)
    # adding rolls changes the random variable
    if model.ROLLS_AVAILABLE:
        ev = sum(simulate(m, i) for i in range(ITERS))/ITERS
        f, fs = model.ROLLS_F, count_rolls[0]/ITERS
        # the largest kakera value k* such that Fk(k*) triggers the roll cutoff
        kp = prob.X[bisect.bisect(m.Fk, f) - 2]
        ev_old, Ez = prob.Ef(prob.R), prob.Ef(prob.B)
        # assume that ROLLS_CYCLE forces k* to be less than E[Zb]
        assert kp < Ez, "mathematical assumption"
        l1 = norm(count_last)
        l2 = [(1 + prob.cmf(prob.Fz, kp))*prob.fz(z) if z > kp
               else prob.fz(z, 2*prob.B) for z in prob.Z]
        ev_l = sum(z*l2[i] for i, z in enumerate(prob.Z))
        # pmf of the kakera values emitted by the last layer
        ldiff(l1, l2, "last layer pmf")
        # expected value calculation is better than comparing the two lists
        adiff(sum(z*l1[i] for i, z in enumerate(prob.Z)), ev_l, "last layer EV")
        ev_new = ev_old + m.p_r(1)*(ev_l - Ez)
        adiff(ev, ev_new, "rolls expected value")
        print(f"using $rolls with a frequency of {fs:.3f}")
        print(f"improves expected value by {ev_new - ev_old:.3f}")
        assert fs <= f, "overusing rolls"
        sys.exit()

    # whether the theoretical model aligns with the empirical expected value
    # no way to know whether this "optimal" value is truly optimal however
    adiff(E(lambda: simulate(m)), prob.Ef(prob.R), "expected value")

    ### testing introspection 
    # probability of getting to r rolls left
    ldiff(norm(count_Fr, ITERS), apply(m.F_r, range(prob.R + 1)), "cdf of f")
    # probability of emitting a value at r rolls left
    ldiff(norm(count_pr), apply(m.p_r, range(prob.R + 1)), "pdf of f")
    # probability of emitting a kakera value of k
    ldiff(norm(count_k), apply(m.p_k, prob.X), "pdf of k")
    # probability distribution times the value equals the expected value 
    adiff(sum(x*m.p_k(x) for x in prob.X), prob.Ef(prob.R), "pmf k vs E")

