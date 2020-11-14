import random, bisect
import prob, model

random.seed(1)
ITERS = 10**5

def sample(X: list, F: list) -> float:
    """ Samples a value from a random variable. """
    p = random.random()
    return X[bisect.bisect(F, p) - 1]

def simulate(m: model.Model) -> float:
    """ Simulates a game. """
    m.reset()
    l = []
    # offset if number of rolls is not a multiple of the batch size
    offset = prob.R % prob.B
    for r in range(prob.R):
        # new batch, reset the seen elements
        # in the case of an offset, remove the offset first
        if len(l) == prob.B or len(l) == offset:
            l, offset = [], -1
        k = sample(prob.X, prob.F)
        l.append(k)
        # give kakera value to the model 
        i = m.update(k)
        if i is not None:
            assert 0 <= i < len(l), "model did not give a valid index"
            return l[i]
    # model didn't claim, kakera value of 0
    return 0

def E(X, iters: int=ITERS) -> float:
    """ Expected value by repeatedly sampling a random variable. """
    return sum(X() for i in range(iters))/iters

if __name__ == "__main__":
    m = model.Model(prob.R)
    print(f"simulated value: {E(lambda: simulate(m)):.3f}")
    print(f"  optimal value: {prob.Ef(prob.R):.3f}")

