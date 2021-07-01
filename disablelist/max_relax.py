from .ilp import *
### find U on the relaxation

if __name__ == "__main__":
    m, x, y, z = model()
    ### objective: maximize d by minimizing the denominator 
    m.objective = xsum(w[i]*(1 - (y[i] - z[i])) for i in range(M))

    m.sense = MINIMIZE
    status = m.optimize(relax=True)
    print(m.objective_value, 1/m.objective_value)

