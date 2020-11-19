import pickle, random, os
from mip import Model, MAXIMIZE, CBC, BINARY, xsum
from problib.data import *

FNAME = "model.lp"

# number of bundles, number of series
N, M = len(bundle_list), len(series_list)
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
m += xsum(x[i] for i in range(N)) == NUM_DISABLE, "number_bundles"
# total sum of bundle sizes less than C = 20,000
m += xsum(s[i]*x[i] for i in range(N)) <= OVERLAP, "capacity_limit"
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
    # disable_list = ['kadokawa future publishing', 'kodansha', 'shogakukan', 'hentai', 'youtube', 'pokémon', 'gangan comics', 'akita shoten', 'web novels', 'houbunsha']
    count = sum(series_dict_wa[x][-1] for x in
                set(s for bundle in disable_list for s in bundle_dict[bundle]))
    total = sum(size[bundle] for bundle in disable_list)

    print(f"disablelist ({len(disable_list)}/10)")
    print(f"{server_disabled + total} disabled ({server_wa + count} $wa)")
    print(f"Overlap limit: {total} / 20000 characters")
    print(f"{count} $wa characters disabled by $disable")
    print(f"$disable {' $'.join(disable_list)}")

