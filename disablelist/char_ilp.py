from .ilp import *
### ILP optimized for disabling the most number of characters

DISABLE_SERIES = True

if __name__ == "__main__":
    m, x, y = model(antidisable=False, disable_series=DISABLE_SERIES,
                    force_disable=False)
    ### objective: maximize number of $wa characters
    m.objective = xsum(w[i]*y[i] for i in range(M))

    status = m.optimize()
    display(antidisable=False, disable_series=DISABLE_SERIES)

