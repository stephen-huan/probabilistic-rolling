import pickle, random, math
from problib.data import *
# the max cover problem, with an additional constraint and weighting
# greedy algorithm on the traditional problem yields a bound of (1 - 1/e):
# https://people.seas.harvard.edu/~yaron/AM221-S16/lecture_notes/AM221_lecture18.pdf

K = 10 # number of sets able to be added
def greedy() -> list:
    """ At each iteration, adds the set which removes the most number. """
    l, seen, count, total = [], set(), 0, 0
    for i in range(K):
        best, add, name, disable_wa, disable = -float("inf"), None, "", 0, 0
        for bundle, series in bundle_dict.items():
            added = set(s for s in series if s not in seen)
            num = size[bundle]
            wa = sum(series_dict_wa[s][-1] for s in added)
            # k = wa
            k = wa + math.exp(disable/20000 - 1)*(-num)*0.75 if num > 0 else 0
            # if total + num > 20000:
            #     continue
            if k > best:
                best, add, name, disable_wa, disable = k, added, bundle, wa, num
        count += disable_wa
        total += disable
        seen |= add
        l.append(name)
    return l, count, total

if __name__ == "__main__":
    disable_list, count, total = greedy()
    print(f"Disabled by server: $wa characters {server_wa} and {server_disabled} total")
    print(f"Disabling {count} $wa characters and {total} characters total")
    print(f"$disable {' $'.join(disable_list)}")

