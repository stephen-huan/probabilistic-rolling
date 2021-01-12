import random, bisect
import cmath, math

EPISLON = 10**-6

### fft implementation

def rev_increment(c: int, m: int) -> int:
    """ Increments a reverse binary counter. """
    i = 1 << (m - 1)
    while c & i > 0:
        c ^= i
        i >>= 1
    return c ^ i

def bit_rev_copy(a: list) -> list:
    """ Constructs an initial order from a by reversing the bits of the index. """
    n, m = len(a), len(a).bit_length() - 1
    A = [0]*n
    c = 0
    for i in range(n):
        A[c] = a[i]
        c = rev_increment(c, m)
    return A

def iter_fft(a: list, inv: bool=False) -> list:
    """ Computes the DFT iteratively. """
    n = len(a)
    A = bit_rev_copy(a)
    for s in range(1, n.bit_length()):
        m = 1 << s
        wm = cmath.exp((-1 if inv else 1)*2*cmath.pi*1j/m)
        for k in range(0, n, m):
            w = 1
            for j in range(m >> 1):
                t = w*A[k + j + (m >> 1)]
                u = A[k + j]
                A[k + j] = u + t
                A[k + j + (m >> 1)] = u - t
                w *= wm
    return A

def inv_iter_fft(a: list) -> list:
    """ Computes the inverse DFT of a. """
    return [x/len(a) for x in iter_fft(a, True)]

def mirror(a: list) -> list:
    """ Mirrors a such that the resulting list has a length which is a power of 2. """
    n, np = len(a), 1 << math.ceil(math.log2(len(a)))
    a += [0]*(np - n)
    return a

def poly_mult(a: list, b: list) -> list:
    """ Multiplies two polynomials via the FFT. """
    m = len(a) + len(b) - 1
    n = max(len(a), len(b))
    # make both lists the same size and degree bound 2n instead of n
    ap = mirror(a + [0]*(n - len(a)) + [0]*n)
    bp = mirror(b + [0]*(n - len(b)) + [0]*n)
    ap, bp = iter_fft(ap), iter_fft(bp)
    return [x.real for x in inv_iter_fft([ap[i]*bp[i] for i in range(len(ap))])]

### probability theory methods

def poly_exp(p: list, k: int) -> list:
    """ Computes p^k, where p is a polynomial and k is an integer. """
    rtn = [1]
    while k > 0:
        # bit on in the binary representation of the exponent
        if k & 1 == 1:
            rtn = poly_mult(rtn, p)
        k >>= 1
        p = poly_mult(p, p)
    return rtn

def get_poly(X: list, p: list) -> list:
    """ Gets the polynomial associated with the r.v. """
    a = [0]*(max(X) + 1)
    for i in range(len(X)):
        a[X[i]] = p[i]
    return a

random.seed(1)
R, ITERS = 10**2, 10**5

def X() -> float:
    """ Sample the random variable X. """
    return random.uniform(0, 1)

def Z(X, iters: int=R) -> float:
    """ Sample the random variable Z. """
    return lambda: sum(X() for i in range(iters))

def sample(X: list, F: list) -> float:
    """ Samples a value from a random variable. """
    p = random.random()
    return X[bisect.bisect(F, p) - 1]

def E(X, iters: int=ITERS) -> float:
    """ Expected value by repeatedly sampling a random variable. """
    return sum(X() for i in range(iters))/iters

if __name__ == "__main__":
    ### continuous case
    print(E(Z(X)))

    ### discrete case 
    X = [   1,    5,  10,   15,   16,   20,  30,   35,   50,  100]
    p = [0.05, 0.08, 0.1, 0.12, 0.17, 0.22, 0.1,  0.1, 0.05, 0.01]
    assert sum(p) == 1
    N = len(X)

    # cmf of X
    F = [0]*(N + 1)
    for i in range(N):
        F[i + 1] = F[i] + p[i]

    print(E(Z(lambda: sample(X, F))))
    pmf = poly_exp(get_poly(X, p), R)
    print(sum(pmf[i]*i for i in range(len(pmf))))

