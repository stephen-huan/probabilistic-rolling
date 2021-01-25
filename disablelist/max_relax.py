import pickle, random, os
from mip import Model, MAXIMIZE, MINIMIZE, CBC, BINARY, xsum
from problib.data import *
### find U on the relaxation

# number of bundles, number of series
N, M = len(bundle_list), len(series_list)
# list[int] mapping bundle/series index -> total characters
s = [size[bundle] for bundle in bundle_list] + \
    [series_dict[series][-1] for series in series_list]
# list[int] mapping series index -> $wa characters
w = [series_dict_wa[series][-1] for series in series_list]

### model and variables
m = Model(sense=MINIMIZE, solver_name=CBC)
# whether the ith bundle/series is disabled
x = [m.add_var(name=f"x{i}", lb=0, ub=1) for i in range(N + M)]
# whether the ith series is included or not
y = [m.add_var(name=f"y{i}", lb=0, ub=1) for i in range(M)]
# whether the ith series is antidisabled or not
z = [m.add_var(name=f"z{i}", lb=0, ub=1) for i in range(M)]

### constraints
# can only disable up to K = 10 bundles, exactly K is faster but less accurate
# change to == K if it doesn't affect the solution and is faster
m += xsum(x) <= NUM_DISABLE, "number_disable"
# total sum of bundle sizes less than C = 20,000
m += xsum(s[i]*x[i] for i in range(len(x))) <= OVERLAP, "capacity_limit"
# can only antidisable up to A = 500 series
m += xsum(z) <= NUM_ANTIDISABLE, "number_antidisable"
for i in range(M):
    series = series_list[i]
    bundles = [x[j] for j in range(N) if series in bundle_dict[bundle_list[j]]]
    # the psuedo-bundle containing just the series
    bundles.append(x[i + N])
    # if yi is included, at least one bundle needs to have it
    m += xsum(bundles) >= y[i], f"inclusion{i}"
    # forcing term, comment out if the metric naturally incentivizes forcing
    for b in bundles:
        m += y[i] >= b, f"forcing{i}_{b.name}"

    # shouldn't antidisable a series if it isn't disabled
    m += z[i] <= y[i], f"antidisable{i}"

### objective: maximize d by minimizing the denominator 
m.objective = xsum(w[i]*(1 - (y[i] - z[i])) for i in range(M))

if __name__ == "__main__":
    m.emphasis = 2 # emphasize optimality
    status = m.optimize()
    print(m.objective_value, 1/m.objective_value)

