import random, os, pickle
import numpy as np
from sklearn.linear_model import LinearRegression
from problib import data, prob, model

N = 10**4                               # number of rows in the dataset
FNAMEX, FNAMEY = "linreg_X", "linreg_y" # names of the files
FNAME_REG, FNAME_COEF = "linreg_model.pickle", "linreg_coef"

random.seed(1)

def sample_series(series: list) -> list:
    """ Picks a random subset from the series to include. """
    row, l = [], []
    for s in series:
        row.append(random.random() <= 0.5)
        # because row represents whether a series is diasbled, add if 0
        if row[-1] == 0:
            l.append(s)
    return row, l

def get_value(X: list, p: list) -> float:
    """ Gets the expected value of the rolls variable for the given r.v. """
    D = {x: i for i, x in enumerate(X)}
    F = prob.prefix_sum(p)
    Fzs = [[pow(v, b) for v in F] for b in range(prob.B + 1)]
    evzs = [prob.prefix_sum([X[i]*(Fzs[b][i + 1] - Fzs[b][i])
            for i in range(len(X))]) for b in range(len(Fzs))]
    p = model.prob
    p.X, p.N, prob.D, p.F, p.Fzs, p.evzs = X, len(X), D, F, Fzs, evzs
    m = model.Model()
    return prob.E([m.p_k(x) for x in X], X)

def dataset(n: int) -> tuple:
    """ Generate a dataset. """
    X, y = [], []
    for i in range(n):
        row, subset = sample_series(series)
        rv, p = data.random_variable(data.char_values(subset))
        yp = get_value(rv, p)
        X.append(row)
        y.append(yp)
    return X, y

series = data.series_list
# load dataset from file
if os.path.exists(f"{FNAMEX}.npy"):
    print("Loading dataset from disk. ")
    X, y = np.load(f"{FNAMEX}.npy"), np.load(f"{FNAMEY}.npy")
# generate data
else:
    print(f"Generating {N} rows...")
    X, y = dataset(N)
    # save dataset for easier model prototyping
    np.save(FNAMEX, X)
    np.save(FNAMEY, y)

# load model from file
if os.path.exists(FNAME_REG):
    print("Loading model from disk.")
    with open(FNAME_REG, "rb") as f:
        reg = pickle.load(f)
# generate model
else:
    print("Generating linear regression model...")
    reg = LinearRegression().fit(X, y)
    with open(FNAME_REG, "wb") as f:
        pickle.dump(reg, f)

# set different seed to make the test set different
random.seed(2)
X_test, y_test = dataset(10**3)
print(f"R^2 score on dataset: {reg.score(X, y)}")
print(f"R^2 score on test: {reg.score(X_test, y_test)}")
# use coefficients of the regression as weights in the ILP's objective
# we don't care about the bias because that's a constant term
np.save(FNAME_COEF, reg.coef_)

