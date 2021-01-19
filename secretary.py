"""
The secretary problem:
Have N candidates, want to pick the best one
(maximize probability of best candidate).
Interview each in a random order, after interview
immediatly choose to accept/reject. Strategy?

Can be shown optimal strategy is of the form
"reject first r, pick first which is better than rejected."
lim n -> infty r = n/e, probabilty of 1/e ~ 0.368 to select best.

If objective is not "highest probability of selecting best applicant"
but each applicant has a value and want to maximize expected value,
problem reduces to Mudae assuming the value distribition is known.
"""
from functools import lru_cache
import matplotlib.pyplot as plt
from math import e

N = 30

@lru_cache(maxsize=None)
def H(n: int) -> float:
    """ Returns Hn = 1 + 1/2 + 1/3 + ... + 1/n. """
    return 0 if n == 0 else 1/n + H(n - 1)

def p(n: int, r: int) -> float:
    """ Probability of being the best if we reject the first r. """
    # don't reject anyone if r = 0, pick first
    return 1/n if r == 0 else r/n*(H(n - 1) - H(r - 1))

def best(n: int) -> int:
    """ Finds the number of people to reject. """
    return max(range(n), key=lambda r: p(n, r))

if __name__ == "__main__":
    size = range(1, N + 1)
    y = list(map(lambda n: p(n, best(n)), size))
    plt.plot(size, y)
    plt.hlines(1/e, 1, N, "orange", label="1/e")
    plt.title("Probability of Selecting the Best")
    plt.ylabel("Probability")
    plt.xlabel("Size (people)")
    plt.legend()
    plt.savefig("graphs/secretary.png")
    plt.show()

