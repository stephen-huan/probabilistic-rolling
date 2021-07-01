import pickle, random, os
import numpy as np
from mip import Model, MAXIMIZE, MINIMIZE, CBC, BINARY, xsum
from problib.data import *
### general ILP giving the structure of the problem

# number of bundles, number of series
N, M = len(bundle_list), len(series_list)
# list[int] mapping bundle/series index -> total characters
s = [size[bundle] for bundle in bundle_list] + \
    [series_dict[series][-1] for series in series_list]
# list[int] mapping series index -> $wa characters
w = [series_dict_wa[series][-1] for series in series_list]

def model(antidisable: bool=True, disable_series: bool=True,
          force_disable: bool=True) -> tuple:
    """ Generates a model. """
    ### model and variables
    m = Model(sense=MAXIMIZE, solver_name=CBC)
    global x, y
    A = M if disable_series else 0
    # whether the ith bundle/series is disabled
    x = [m.add_var(name=f"x{i}", var_type=BINARY) for i in range(N + A)]
    # whether the ith series is included or not
    y = [m.add_var(name=f"y{i}", var_type=BINARY) for i in range(M)]
    if antidisable:
        global z
        # whether the ith series is antidisabled or not
        z = [m.add_var(name=f"z{i}", var_type=BINARY) for i in range(M)]

    ### constraints
    # can only disable up to K = 10 bundles, exactly K is faster but inaccurate
    # change to == K if it doesn't affect the solution and is faster
    m += xsum(x) <= NUM_DISABLE, "number_disable"
    # total sum of bundle sizes less than C = 20,000
    m += xsum(s[i]*x[i] for i in range(len(x))) <= OVERLAP, "capacity_limit"
    if antidisable:
        # can only antidisable up to A = 500 series
        m += xsum(z) <= NUM_ANTIDISABLE, "number_antidisable"
    for i in range(M):
        yi, name = y[i], series_list[i]
        bundles = [x[j] for j in range(N)
                   if name in bundle_dict[bundle_list[j]]]
        if disable_series:
            # the psuedo-bundle containing just the series
            bundles.append(x[i + N])
        # if yi is included, at least one bundle needs to have it
        m += xsum(bundles) >= yi, f"inclusion{i}"
        # forcing term, comment out if the objective incentivizes forcing
        if force_disable:
            m += xsum(bundles) <= len(bundles)*yi, f"forcing{i}"
        # shouldn't antidisable a series if it isn't disabled
        if antidisable:
            m += z[i] <= yi, f"antidisable{i}"

    m.emphasis = 2 # emphasize optimality

    return (m, x, y, z) if antidisable else (m, x, y)

def display(antidisable: bool=True, disable_series: bool=True):
    """ Displays the result of the optimization. """
    tol = 0.99
    A = M if disable_series else 0
    disable_list = [bundle_list[i] for i in range(N) if x[i].x >= tol] + \
        [series_list[i - N] for i in range(N, N + A) if x[i].x >= tol]
    total, count = get_size(disable_list), get_wa(disable_list)

    print(f"disablelist ({len(disable_list)}/{NUM_DISABLE})")
    print(f"{server_disabled + total} disabled ({server_wa + count} $wa)")
    print(f"Overlap limit: {total} / {OVERLAP} characters")
    print(f"{count} $wa characters disabled by $disable")
    print(f"$disable {' $'.join(disable_list)}")

    if antidisable:
        antidisable_list = [series_list[i] for i in range(M) if z[i].x >= tol]
        count_anti = get_wa(antidisable_list)
        print(f"antidisablelist ({len(antidisable_list)}/{NUM_ANTIDISABLE})")
        print(f"{count_anti} antidisabled characters")
        print(f"$antidisable {' $'.join(antidisable_list)}")

if __name__ == "__main__":
    ### objective: load coefficients from numpy array 
    coef = np.load("linreg_coef.npy")
    m.objective = xsum(coef[i]*(y[i] - z[i]) for i in range(M))

    status = m.optimize()
    display()

