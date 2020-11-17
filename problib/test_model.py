import random, bisect, sys
from . import prob, model
from .testing import norm, apply, adiff, fdiff

random.seed(1)
ITERS = 10**5
prob.R, prob.B = 30, 10
model.ROLLS_AVAILABLE, model.ROLLS_CYCLE = True, 10
model.ROLLS_F = 1/model.ROLLS_CYCLE

count_Fr = [0]*(prob.R + 1)
count_pr = [0]*(prob.R + 1)
count_k  = [0]*prob.N
count_rolls = [0]
count_last = [0]*prob.N

def sample(X: list=prob.X, F: list=prob.F) -> float:
    """ Samples a value from a random variable. """
    p = random.random()
    return X[bisect.bisect(F, p) - 1]

def simulate(m: model.Model=model.Model(), index: int=0) -> float:
    """ Simulates a game. """
    m.reset()
    # give the model a roll every ROLLS_CYCLE claim iterations
    if model.ROLLS_AVAILABLE and index % model.ROLLS_CYCLE == 0:
        m.rolls_left += 1
    lowest = prob.R
    l = []
    # offset if number of rolls is not a multiple of the batch size
    offset = prob.R % prob.B
    # in the case of an offset, remove the offset first
    size = offset if offset > 0 else prob.B
    r = prob.R
    while r > 0:
        lowest = min(lowest, r)
        # new batch, reset seen and assume offset has been taken care of
        if len(l) == size:
            l, size = [], prob.B
        k = sample()
        l.append(k)
        # give kakera value to the model 
        i = m.update(k)
        if i is not None:
            if i == model.ROLLS:
                assert model.ROLLS_AVAILABLE, "$rolls is not allowed"
                assert m.rolls_left > 0, "model doesn't have available rolls"
                count_rolls[0] += 1
                # $rolls resets the batch instead of adding the batch size
                delta = prob.upper(r, prob.B) - r + 1
                r += delta
                size += delta
                m.rolls_left -= 1
            else:
                assert 0 <= i < len(l), "model did not give a valid index"
                count_pr[r] += 1
                count_k[prob.D[l[i]]] += 1
                if r == 1:
                    count_last[prob.D[l[i]]] += 1
                for r in range(lowest, prob.R + 1):
                    count_Fr[r] += 1
                return l[i]
        r -= 1
    # model didn't claim, kakera value of 0
    return 0

def E(X, iters: int=ITERS) -> float:
    """ Expected value by repeatedly sampling a random variable. """
    return sum(X() for i in range(iters))/iters

if __name__ == "__main__":
    m = model.Model(prob.R, prob.B, model.ROLLS_AVAILABLE, model.ROLLS_CYCLE)
    # adding rolls changes the random variable
    if model.ROLLS_AVAILABLE:
        ev = sum(simulate(m, i) for i in range(ITERS))/ITERS
        f, fs = model.ROLLS_F, count_rolls[0]/ITERS
        ev_old, Ez = prob.Ef(prob.R, prob.B), prob.Ef(prob.B, prob.B)
        assert fs <= f, "overusing rolls"
        # assume that ROLLS_CYCLE forces k* to be less than E[Zb]
        assert m.kp < Ez, "simplifying mathematical assumption"

        ### testing introspection
        # these should also work if we assume we $rolls on the last layer
        fdiff(count_Fr, m.F_r, range(prob.R + 1), "cdf of f", True)
        fdiff(count_pr, m.p_r, range(prob.R + 1), "pdf of f")
        # pmf of the kakera values emitted by the last layer
        fdiff(count_last, m.p_last, prob.X, "last layer pmf")
        # changed pmf of emitting a kakera value overall as a result
        fdiff(count_k, m.p_k, prob.X, "pdf of k")

        ### expected value
        ev_new = ev_old + m.p_r(1)*(prob.E(apply(m.p_last)) - Ez)
        adiff(ev, ev_new, "rolls expected value")
        print(f"using $rolls with a frequency of {fs:.3f}")
        print(f"improves expected value by {ev_new - ev_old:.3f}")
        sys.exit()

    # whether the theoretical model aligns with the empirical expected value
    # no way to know whether this "optimal" value is truly optimal however
    adiff(E(lambda: simulate(m)), prob.Ef(prob.R, prob.B), "expected value")

    ### testing introspection 
    # probability of getting to r rolls left
    fdiff(count_Fr, m.F_r, range(prob.R + 1), "cdf of f", True)
    # probability of emitting a value at r rolls left
    fdiff(count_pr, m.p_r, range(prob.R + 1), "pdf of f")
    # probability of emitting a kakera value of k
    fdiff(count_k, m.p_k, prob.X, "pdf of k")
    # expected value of the kakera pmf is the expected value of the model 
    adiff(prob.E(apply(m.p_k)), prob.Ef(prob.R, prob.B), "pmf k vs E")

