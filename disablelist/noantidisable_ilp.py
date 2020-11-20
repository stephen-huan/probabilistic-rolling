import pickle, random, os
from mip import Model, MAXIMIZE, CBC, BINARY, xsum
from problib.data import *
from problib.prob import E
### ILP optimized for expected value
"""
technique described here: http://lpsolve.sourceforge.net/5.1/ratio.htm
specific problem is that of mixed-integer linear fractional programming,
solved with the reformulation-linerization method:
https://optimization.mccormick.northwestern.edu/index.php/Mixed-integer_linear_fractional_programming_(MILFP)
"""
DISABLE_SERIES = True # whether to disable series
# number of bundles, number of series
N, M = len(bundle_list), len(series_list)
# list[int] mapping bundle/series index -> total characters
s = [size[bundle] for bundle in bundle_list] + \
    [series_dict[series][-1] for series in series_list]
# list[int] mapping series index -> $wa characters
w = [series_dict_wa[series][-1] for series in series_list]
# list[int] mapping series index -> total kakera value
t = [series_dict_wa[series][1] for series in series_list]
A = M if DISABLE_SERIES else 0

### model and variables
m = Model(sense=MAXIMIZE, solver_name=CBC)
# lower and upper bounds on the denominator for Glover linearization 
L, U = 0, sum(w)
# also double each list of variables, first are binary, second continuous 
# whether the ith bundle/series is disabled
x = [[m.add_var(name=f"x{i}", var_type=BINARY) for i in range(N + A)],
     [m.add_var(name=f"xp{i}", lb=L, ub=U) for i in range(N + A)]]
# whether the ith series is included or not
y = [[m.add_var(name=f"y{i}", var_type=BINARY) for i in range(M)],
     [m.add_var(name=f"yp{i}", lb=L, ub=U) for i in range(M)]]
# denominator for the Charnes-Cooper transformation
d = m.add_var(name="denominator", lb=0, ub=1)

### constraints
# can only disable up to K = 10 bundles, exactly K is faster but less accurate
# change to <= K if it gives a better solution
m += xsum(x[1]) <= NUM_DISABLE*d, "number_disable"
# total sum of bundle sizes less than C = 20,000
m += xsum(s[i]*x[1][i] for i in range(len(x))) <= OVERLAP*d, "capacity_limit"
for i in range(M):
    name = series_list[i]
    bundles = [x[1][j] for j in range(N) if name in bundle_dict[bundle_list[j]]]
    if DISABLE_SERIES:
        # the psuedo-bundle containing just the series
        bundles.append(x[1][i + N])
    # if yi is included, at least one bundle needs to have it
    m += xsum(bundles) >= y[1][i], f"inclusion{i}"
    # forcing term, comment out if the metric naturally incentivizes forcing
    for b in bundles:
        m += y[1][i] >= b, f"forcing{i}_{b.name}"

# Glover linearization constraints in order to force
# the continuous variables to act like a product 
for k, var_list in enumerate([x, y]):
    for i in range(len(var_list[0])):
        xi, zi = var_list[0][i], var_list[1][i]
        m += L*xi <= zi,  f"x{k}{i}_0l"
        m += zi <= U*xi, f"x{k}{i}_0r"
        m += d - U*(1 - xi) <= zi, f"x{k}{i}_1l"
        m += zi <= d - L*(1 - xi), f"x{k}{i}_1r"

# denominator of the expected value
m += xsum(w[i]*(d - y[1][i]) for i in range(M)) == 1, "denominator"

### objective: maximize expected value of the remaining characters
# numerator of the expected value, denominator has been accounted for
m.objective = xsum(t[i]*(d - (y[1][i])) for i in range(M))

if __name__ == "__main__":
    m.emphasis = 2   # emphasize optimality
    m.preprocess = 1 # don't preprocess if it introduces error
    status = m.optimize()
    disable_list = [bundle_list[i] for i in range(N) if x[0][i].x >= 0.99] + \
        [series_list[i - N] for i in range(N, N + A) if x[0][i].x >= 0.99]
    antidisable_list = []
    count = sum(series_dict_wa[s][-1] for s in get_series(disable_list))
    total = sum(size[bundle] if bundle in size else series_dict_wa[bundle][-1]
                for bundle in disable_list)
    count_anti = sum(series_dict_wa[s][-1] for s in antidisable_list)

    X, p = random_variable(character_values(disable_list, antidisable_list))
    print(f"expected value: {E(p, X):.3f}")

    print(f"disablelist ({len(disable_list)}/{NUM_DISABLE})")
    print(f"{server_disabled + total} disabled ({server_wa + count} $wa)")
    print(f"Overlap limit: {total} / {OVERLAP} characters")
    print(f"{count} $wa characters disabled by $disable")
    print(f"$disable {' $'.join(disable_list)}")

    print(f"antidisablelist ({len(antidisable_list)}/{NUM_ANTIDISABLE})")
    print(f"{count_anti} antidisabled characters")
    print(f"$antidisable {' $'.join(antidisable_list)}")

