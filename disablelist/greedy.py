import pickle, random, math
# the max cover problem, with an additional constraint and weighting
# greedy algorithm on the traditional problem yields a bound of (1 - 1/e):
# https://people.seas.harvard.edu/~yaron/AM221-S16/lecture_notes/AM221_lecture18.pdf

with open("data/bundle_info.p", "rb") as f:
    # maps bundles -> List[str] of series
    bundle_dict = pickle.load(f)
with open("data/total_series_info.p", "rb") as f:
    # maps series -> Tuple(top_kak, total_kak, total_char)
    series_dict = pickle.load(f)
with open("data/wa_series_info.p", "rb") as f:
    # maps series -> Tuple(top_wa_kak, total_wa_kak, total_wa)
    series_dict_wa = pickle.load(f)

# compute sizes of each bundle
# number disabled is irrespective of overlap, counts it twice
size = {bundle: sum(series_dict[s][-1] for s in series)
        for bundle, series in bundle_dict.items()}

# disable server bundles
server_disabled_list = ["Western", "Horror Genre", "Disturbing Imagery"]
server_seen = set(x for b in server_disabled_list for x in bundle_dict[b])
for bundle, series in bundle_dict.items():
    bundle_dict[bundle] = set(s for s in series if s not in server_seen)
server_wa, server_disabled = map(sum,
zip(*[(series_dict_wa[s][-1], series_dict[s][-1]) for s in server_seen]))
for s in server_seen:
    del series_dict[s]
    del series_dict_wa[s]

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

