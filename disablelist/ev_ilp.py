import pickle, random, os
from mip import Model, MAXIMIZE, CBC, BINARY, xsum

FNAME = "model.lp"

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
server_disabled_list = ["Western", "Disturbing Imagery"]
server_seen = set(x for b in server_disabled_list for x in bundle_dict[b])
for bundle, series in bundle_dict.items():
    bundle_dict[bundle] = set(s for s in series if s not in server_seen)
server_wa, server_disabled = map(sum,
zip(*[(series_dict_wa[s][-1], series_dict[s][-1]) for s in server_seen]))
for s in server_seen:
    del series_dict[s]
    del series_dict_wa[s]

bundle_list, series_list = list(bundle_dict.keys()), list(series_dict.keys())
# number of bundles, number of series, and number of bundles able to be added
N, M, K, C = len(bundle_list), len(series_list), 10, 20000
# list[int] mapping bundle index -> total characters
s = [size[bundle] for bundle in bundle_list]
# list[int] mapping series index -> $wa characters
w = [series_dict_wa[series][-1] for series in series_list]

### model and variables
m = Model(sense=MAXIMIZE, solver_name=CBC)
# whether the ith bundle is included or not
x = [m.add_var(name=f"x{i}", var_type=BINARY) for i in range(N)]
# whether the ith series is included or not
y = [m.add_var(name=f"y{i}", var_type=BINARY) for i in range(M)]

### constraints
# can only pick K = 10 bundles
# exactly K is faster but less accurate
# change to <= K if it gives a better solution
m += xsum(x[i] for i in range(N)) == K, "number_bundles"
# total sum of bundle sizes less than C = 20,000
m += xsum(s[i]*x[i] for i in range(N)) <= C, "capacity_limit"
# if yi is included, at least one bundle needs to have it
for i in range(M):
    m += xsum(x[j] for j in range(N) if series_list[i]
              in bundle_dict[bundle_list[j]]) >= y[i], f"inclusion{i}"

### objective: mmaximize expected value of the remaining characters
# technique described here: http://lpsolve.sourceforge.net/5.1/ratio.htm
m.objective = xsum(w[i]*y[i] for i in range(M))

if __name__ == "__main__":
    # emphasize optimality
    m.emphasis = 2
    status = m.optimize()
    disable_list = [bundle_list[i] for i in range(N) if x[i].x >= 0.99]
    # disable_list = ['Kadokawa Future Publishing', 'Kodansha', 'Shogakukan', 'Hentai', 'YouTube', 'Pokémon', 'Gangan Comics', 'Akita Shoten', 'Web Novels', 'Houbunsha']
    count = sum(series_dict_wa[x][-1] for x in
                set(s for bundle in disable_list for s in bundle_dict[bundle]))
    total = sum(size[bundle] for bundle in disable_list)

    print(f"diablelist ({len(disable_list)}/10)")
    print(f"{server_disabled + total} disabled ({server_wa + count} $wa)")
    print(f"Overlap limit: {total} / 20000 characters")
    print(f"{count} $wa characters disabled by $disable")
    print(f"$disable {' $'.join(disable_list)}")

