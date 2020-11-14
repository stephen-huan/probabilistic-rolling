import random, bisect
"""
continous random variable X ~ [0, 1], f(x) = 1 and F(x) = x
Z_n = max of n samples of X
F_z(x) = p(max of n samples <= x) = F(x)^n
p_z(x) = dF_z/dx = nF(x)^{n - 1} * f(x)

p_z(x) = nx^{n - 1}
so E[x] = n/(n + 1)
"""
random.seed(1)
R, ITERS = 10, 10**5

def X() -> float:
    """ Sample the random variable X. """
    return random.uniform(0, 1)

def Z(X, iters: int=R) -> float:
    """ Sample the random variable Z. """
    return lambda: max(X() for i in range(iters))

def sample(X: list, F: list) -> float:
    """ Samples a value from a random variable. """
    p = random.random()
    return X[bisect.bisect(F, p) - 1]

def pz(z):
    """ pmf of Z """
    i = bisect.bisect(X, z)
    return pow(F[i], R) - pow(F[i - 1], R)

def E(X, iters: int=ITERS) -> float:
    """ Expected value by repeatedly sampling a random variable. """
    return sum(X() for i in range(iters))/iters

if __name__ == "__main__":
    ### continuous case
    print(E(Z(X)))
    print(R/(R + 1))

    ### discrete case 
    X = [   1,    5,  10,   15,   16,   20,  30,   35,   50,  100]
    p = [0.05, 0.08, 0.1, 0.12, 0.17, 0.22, 0.1,  0.1, 0.05, 0.01]
    assert sum(p) == 1
    N = len(X)

    # cmf of X
    F = [0]*(N + 1)
    for i in range(N):
        F[i + 1] = F[i] + p[i]

    Fz = [0]*(N + 1)
    for i in range(N):
        Fz[i + 1] = Fz[i] + pz(X[i])

    # print(F)
    # print(Fz)
    # print([pow(f, R) for f in F])

    print(sum(pz(x)*x for x in X))
    print(E(Z(lambda: sample(X, F))))

