import pickle, random, os
from mip import Model, MAXIMIZE, CBC, BINARY, xsum
from problib.data import *

FNAME = "model.lp"

# number of bundles, number of series
N, M = len(bundle_list), len(series_list)
# list[int] mapping bundle/series index -> total characters
s = [size[bundle] for bundle in bundle_list] + \
    [series_dict[series][-1] for series in series_list]
# list[int] mapping series index -> $wa characters
w = [series_dict_wa[series][-1] for series in series_list]

### model and variables
m = Model(sense=MAXIMIZE, solver_name=CBC)
# whether the ith bundle/series is disabled
x = [m.add_var(name=f"x{i}", var_type=BINARY) for i in range(N + M)]
# whether the ith series is included or not
y = [m.add_var(name=f"y{i}", var_type=BINARY) for i in range(M)]

### constraints
# can only pick up to K = 10 bundles, exactly K is faster but less accurate
# change to <= K if it gives a better solution
m += xsum(x) == NUM_DISABLE, "number_bundles"
# total sum of bundle sizes less than C = 20,000
m += xsum(s[i]*x[i] for i in range(len(x))) <= OVERLAP, "capacity_limit"
for i in range(M):
    series = series_list[i]
    bundles = [x[j] for j in range(N) if series in bundle_dict[bundle_list[j]]]
    # the psuedo-bundle containing just the series
    bundles.append(x[i + N])
    # if yi is included, at least one bundle needs to have it
    m += xsum(bundles) >= y[i], f"inclusion{i}"
    # forcing term, comment out if the metric naturally incentivizes forcing
    # for b in bundles:
    #     m += y[i] >= b, f"forcing{i}-{b.name}"

### objective: maximize number of $wa characters
m.objective = xsum(w[i]*y[i] for i in range(M))

if __name__ == "__main__":
    m.emphasis = 2 # emphasize optimality
    status = m.optimize()
    disable_list = [bundle_list[i] for i in range(len(x)) if x[i].x >= 0.99]
    # disable_list = ['kadokawa future publishing', 'shueisha', 'kodansha', 'shogakukan', 'akita shoten', 'houbunsha', 'virtual youtubers', 'young gangan', 't-rex', 'comic ryu']
    count = sum(series_dict_wa[s][-1] for s in get_series(disable_list))
    total = sum(size[bundle] if bundle in size else series_dict_wa[bundle][-1]
                for bundle in disable_list)

    print(f"disablelist ({len(disable_list)}/10)")
    print(f"{server_disabled + total} disabled ({server_wa + count} $wa)")
    print(f"Overlap limit: {total} / 20000 characters")
    print(f"{count} $wa characters disabled by $disable")
    print(f"$disable {' $'.join(disable_list)}")

