import random, bisect, sys
import prob

def sample(X: list, F: list) -> float:
    """ Samples a value from a random variable. """
    p = random.random()
    return X[bisect.bisect(F, p) - 1]

if __name__ == "__main__":
    random.seed(1)
    game, total = 0, 0
    while True:
        l, v = [], 0
        print(f"Starting game #{game + 1}")
        for r in range(prob.R):
            if r != 0 and r % prob.B == 0:
                print("Batch over. Cannot claim characters from before. ")
                l = []
            k = sample(prob.X, prob.F)
            l.append(k)
            b, p = r//prob.B, r % prob.B
            s = input(f"Batch {b + 1}, roll {p + 1}: Rolled a character with kakera value {k}. ")
            try:
                c = int(s)
            except:
                c = None
            if c is not None:
                try:
                    v = l[c - 1]
                    total += v
                    print(f"Claimed character {c}, with kakera value {v}. ")
                    break
                except:
                    pass
        game += 1
        print(f"Game over. Value of {v}")
        print(f"Running average over all games: {total/game:.3f}")

