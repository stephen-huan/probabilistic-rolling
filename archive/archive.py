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

### data.py
# manually fixing Avik's regex which breaks for characters with a * in the name 
series_char = load_data("wa_series_info")
series_char["HARDCORE TANO*C"]["chars"] = {"DORO*C": (43, False)}
series_char["Utaite"]["chars"]["*namirin"] = (40, False)
print(len(series_char["Utaite"]["chars"]))
with open("temp.pickle", "wb") as f:
    pickle.dump(series_char, f)

### model.py
# sophisticated surgery to try to find a systematic way to get closer to 1/8 

            f = 1 - prob.cmf(self.Fz, self.kp)
            fp = f + self.fz(self.kp)
            l, r = 0, ROLLS_MAX
            while l < r:
                m = (l + r - 1)>>1
                p = 1/f - self.__sum(f, m) + self.__sum(fp, m)
                if self.p_r(1)*(1 - fp)*p <= ROLLS_F:
                    l, r = l, m
                else:
                    l, r = m + 1, r

    def __sum(self, x: float, n: int) -> float:
        """ Computes sum^n_{i = 1} ix(1 - x)^{i - 1}. """
        return x*(1 + pow(1 - x, n)*(n*(1 - x) - (n + 1)))/(x*x)

