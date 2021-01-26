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
NUM_BUNDLES = 30                           # reduce number of variables
DISABLE_SERIES, ANTIDISABLE = False, True  # whether to [anti]disable series
# number of bundles, number of series
N, M = len(bundle_list), len(series_list)
bundle_list.sort(key=lambda bundle: -size[bundle])
NUM_BUNDLES = N = min(NUM_BUNDLES, N)
bundle_list = bundle_list[:N]
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
# upper bound determined with linear programming
L, U = 0, 0.0002
# also double each list of variables, first are binary, second continuous 
# whether the ith bundle/series is disabled
x = [m.add_var(name=f"x{i}", var_type=BINARY) for i in range(N + A)]
# whether the ith series is included or not
y = [[m.add_var(name=f"y{i}", var_type=BINARY) for i in range(M)],
     [m.add_var(name=f"yp{i}", lb=L, ub=U) for i in range(M)]]
# whether the ith series is antidisabled or not
z = [[m.add_var(name=f"z{i}", var_type=BINARY) for i in range(M)],
     [m.add_var(name=f"zp{i}", lb=L, ub=U) for i in range(M)]]
# denominator for the Charnes-Cooper transformation
d = m.add_var(name="denominator", lb=L, ub=U)

### constraints
# can only disable up to K = 10 bundles, exactly K is faster but less accurate
# change to <= K if it gives a better solution
m += xsum(x) == NUM_DISABLE, "number_disable"
# total sum of bundle sizes less than C = 20,000
m += xsum(s[i]*x[i] for i in range(len(x))) <= OVERLAP, "capacity_limit"
# can only antidisable up to A = 500 series
m += xsum(z[0]) <= NUM_ANTIDISABLE, "number_antidisable"
for i in range(M):
    yi, name = y[0][i], series_list[i]
    bundles = [x[j] for j in range(N) if name in bundle_dict[bundle_list[j]]]
    if DISABLE_SERIES:
        # the psuedo-bundle containing just the series
        bundles.append(x[i + N])
    # if yi is included, at least one bundle needs to have it
    m += xsum(bundles) >= yi, f"inclusion{i}"
    # forcing term, comment out if the metric naturally incentivizes forcing
    if len(bundles) <= 3:
        for b in bundles:
            m += yi >= b, f"forcing{i}_{b.name}"
    else:
        # create yp = (x1 + x2 + ... + xj) yi
        g, L1, U1 = xsum(bundles), 0, len(bundles)
        yp = m.add_var(name=f"forcing{i}", lb=L1, ub=U1)
        # m += L1*yi <= yp, f"forcing{i}_0l"
        m += yp <= U1*yi, f"forcing{i}_0r"
        # m += g - U1*(1 - yi) <= yp, f"forcing{i}_1l"
        # m += yp <= g - L1*(1 - yi), f"forcing{i}_1r"
        # m += yp >= g, "forcing{i}_final"
        m += yp == g, "forcing{i}_final"

    # shouldn't antidisable a series if it isn't disabled
    m += z[0][i] <= y[0][i], f"antidisable{i}"

# Glover linearization constraints in order to force
# the continuous variables to act like a product 
for k, var_list in enumerate([y, z]):
    for i in range(len(var_list[0])):
        xi, zi = var_list[0][i], var_list[1][i]
        # m += L*xi <= zi, f"x{k}{i}_0l"
        m += zi <= U*xi, f"x{k}{i}_0r"
        m += d - U*(1 - xi) <= zi, f"x{k}{i}_1l"
        m += zi <= d - L*(1 - xi), f"x{k}{i}_1r"

# denominator of the expected value
m += xsum(w[i]*(d - (y[1][i] - z[1][i])) for i in range(M)) == 1, "denominator"

# if not antidisabling, turn each antidisable off 
if not ANTIDISABLE:
    for i in range(len(z[0])):
        m += z[0][i] == 0, f"{zi.name}0"
        m += z[1][i] == 0, f"{zi.name}1"

### objective: maximize expected value of the remaining characters
# numerator of the expected value, denominator has been accounted for
m.objective = xsum(t[i]*(d - (y[1][i] - z[1][i])) for i in range(M))

if __name__ == "__main__":
    m.emphasis = 2   # emphasize optimality
    m.preprocess = 1 # don't preprocess if it introduces error
    status = m.optimize()
    disable_list = [bundle_list[i] for i in range(N) if x[i].x >= 0.99] + \
        [series_list[i - N] for i in range(N, N + A) if x[i].x >= 0.99]
    antidisable_list = [series_list[i] for i in range(M) if z[0][i].x >= 0.99]
    total = get_size(disable_list)
    count, count_anti = get_wa(disable_list), get_wa(antidisable_list)

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

