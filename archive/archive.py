### ilp.py

# save model to file
m.write(FNAME)
# not sure why file loading is broken
if os.path.exists(FNAME) and False:
    m.read(FNAME)
else:
    modify_model(m)

### prob.py

@lru_cache(maxsize=None)
def _E(i: int, r: int) -> float:
    """ E[X_r], where r = T - t (rolls left). """
    # if r = 0, then we're out of samples and has a constant value of 0 
    return 0 if r == 0 else capped(rv[i], pmf[i], _E(i, r - 1))

def E(i: int, T: int, t: int) -> float:
    """ E[X_t], where X_t is X after being sampled t times, with a max of T. """
    return _E(i, T - t)

# slow pmf definitions
@lru_cache(maxsize=None)
def E(i: int, r: int) -> float:
    """ E[X_r], where X_r is X with possibly r more samples. """
    # if r = 0, then we're out of samples and has a constant value of 0
    return 0 if r == 0 else capped_slow(rv[i], pmf[i], E(i, r - 1))

rv, pmf = [X, Z], [f, fz]

# cmf of Z is just the power of each term in the cmf of X
Fz = [pow(v, B) for v in F]
# expected value prefix sum similar to X 
evz = [0]*(N + 1)
for i in range(N):
    evz[i + 1] = evz[i] + X[i]*(Fz[i + 1] - Fz[i])

