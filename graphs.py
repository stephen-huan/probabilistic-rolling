import matplotlib.pyplot as plt
import numpy as np
from problib.prob import *
from problib import model

ROLLS = True  # whether to include the $rolls model
STEM  = False # whether to use a stem plot

graphs = [None] + [0]*20
graphs[1] = 1
fig = plt.figure(tight_layout=True)

def graph_rv(X: list, p: list, i: int=0, label: str=None) -> None:
    """ Graphs a random variable using a stem plot. """
    if STEM:
        plt.stem(X, p, linefmt=f"C{i}-", markerfmt=f"C{i}o", label=label)
    else:
        plt.plot(X, p, label=label)
    plt.ylabel("Probability")
    plt.xlabel("Value")

def model_pmf(r: int=R, b: int=B,
        ra: bool=model.ROLLS_AVAILABLE, rc: int=model.ROLLS_CYCLE) -> float:
    """ pmf for the given parameterized model. """
    m = model.Model(r, b, ra, rc)
    return [m.p_k(x) for x in X]

ev, var = lambda *args: E(model_pmf(*args)), lambda *args: Var(model_pmf(*args))

### Graph 1: pmf of X
g = 1
if graphs[g]:
    graph_rv(X, p)
    plt.title("Random Variable X")
    plt.savefig(f"graphs/graph{g:02}.png")
    plt.show()

### Graph 2: pmf of Zn
g = 2
if graphs[g]:
    B = 10
    for i, b in enumerate([1, 5, B]):
        graph_rv(Z, [fz(z, b) for z in Z], i, f"Z with batch size {b}")
    plt.title("Random Variable Zs")
    plt.legend()
    plt.savefig(f"graphs/graph{g:02}.png")
    plt.show()

### Graph 3: pmf of the model 
g = 3
if graphs[g]:
    R, B = 30, 10
    m = model.Model(R)
    graph_rv(X, p, 0, "X")
    graph_rv(Z, [fz(z, B) for z in Z], 1, f"Z with batch size {B}")
    graph_rv(X, model_pmf(R, B, False), 2, f"Model pmf over {R} rolls")
    if ROLLS:
        graph_rv(X, model_pmf(R, B, True), 3, f"Model pmf with $rolls")
    plt.title("Random Variable of the Model")
    plt.legend()
    plt.savefig(f"graphs/graph{g:02}{'_rolls' if ROLLS else ''}.png")
    plt.show()

### Graph 4: the E[t] dropoff over time
g = 4
if graphs[g]:
    R, B = 500, 10
    BATCHES = R//B
    x, y = list(range(R + 1)), [ev(r, 1, False) for r in range(R + 1)]
    # xz = [b*B for b in range(BATCHES + 1)]
    # yz = [Er(1, b) for b in range(BATCHES + 1)]
    yf = [ev(r, B, False) for r in x]
    yr = [ev(r, B, True) for r in x[1:]]
    plt.plot(x, y, label="batch size of 1")
    # plt.plot(xz, yz, label=f"batch size of {B}")
    plt.plot(x, yf, label=f"batch size of {B}")
    if ROLLS:
        plt.plot(x[1:], yr, label=f"with $rolls")
    plt.title("Expected Value over Time")
    plt.ylabel("Expected Value (kakera)")
    plt.xlabel("Time (rolls)")
    plt.legend()
    plt.savefig(f"graphs/graph{g:02}{'_rolls' if ROLLS else ''}.png")
    plt.show()

### Graph 5: expected value of the model over batch size
g = 5
if graphs[g]:
    R, B = 50, 52
    x, y = list(range(1, B + 1)), [ev(R, b, False) for b in range(1, B + 1)]
    plt.plot(x, y)
    if ROLLS:
        yr = [ev(R, b, True) for b in range(1, B + 1)]
        plt.plot(x, yr, label=f"with $rolls")
        plt.legend()
    plt.title("Model Expected Value over Batch Size")
    plt.ylabel("Expected Value (kakera)")
    plt.xlabel("Batch Size")
    plt.savefig(f"graphs/graph{g:02}{'_rolls' if ROLLS else ''}.png")
    plt.show()

### Graph 6: expected value of the model over rolls and batch size
g = 6
if graphs[g]:
    R, B = 100, 100
    grid = [[(r, b) for b in range(1, B + 1)] for r in range(1, R + 1)]
    z = [[ev(r, b, False) for r, b in row] for row in grid]
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(*zip(*[zip(*row) for row in grid]), np.array(z),
                    cmap="viridis")
    ax.set_title("Expected Value over Rolls and Batch Size")
    ax.set_zlabel("Expected Value")
    plt.ylabel("Batch Size")
    plt.xlabel("Rolls")
    plt.savefig(f"graphs/graph{g:02}.png")
    plt.show()

### Graph 7: the derivative E[t] with respect to t
g = 7
if graphs[g]:
    R = 100
    x, yf = list(range(R + 1)), list(map(Ef, range(R + 1)))
    yp = [yf[i + 1] - yf[i] for i in range(len(yf) - 1)]
    plt.plot(x[1:], yp)
    plt.title("Change over Time")
    plt.ylabel("Change in Expected Value (kakera)")
    plt.xlabel("Time (rolls)")
    plt.savefig(f"graphs/graph{g:02}.png")
    plt.show()

### Graph 8: unit price of rolls
g = 8
if graphs[g]:
    grid = [[(r, k) for k in range(1, 11)] for r in range(R + 1)]
    z = [[price(r, k)/k for r, k in row] for row in grid]
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(*zip(*[zip(*row) for row in grid]), np.array(z),
                    cmap="viridis")
    ax.set_title("Roll Pricing Model")
    ax.set_zlabel("Unit Price of Rolls (Kakera/Roll)")
    ax.set_ylabel("Number of Rolls Sold")
    ax.set_xlabel("Buyer's Number of Rolls")
    plt.savefig(f"graphs/graph{g:02}.png")
    plt.show()

### Graph 9: variance of the model over rolls
g = 9
if graphs[9]:
    R, B = 2000, 2000
    x, y = list(range(R + 1)), [var(r, B, False) for r in range(R + 1)]
    plt.plot(x, y)
    if ROLLS:
        yr = [var(r, B, True) for r in range(1, R + 1)]
        plt.plot(x[1:], yr, label=f"with $rolls")
        plt.legend()
    plt.title("Model Variance over Time")
    plt.ylabel("Variance (kakera^2)")
    plt.xlabel("Rolls")
    plt.savefig(f"graphs/graph{g:02}{'_rolls' if ROLLS else ''}.png")
    plt.show()

### Graph 10: variance over batch size 
g = 10
if graphs[g]:
    R, B = 100, 100
    x, y = list(range(1, B + 1)), [var(R, b, False) for b in range(1, B + 1)]
    plt.plot(x, y)
    if ROLLS:
        yr = [var(R, b, True) for b in range(1, B + 1)]
        plt.plot(x, yr, label=f"with $rolls")
        plt.legend()
    plt.title("Model Variance over Batch Size")
    plt.ylabel("Variance (kakera^2)")
    plt.xlabel("Batch Size")
    plt.savefig(f"graphs/graph{g:02}{'_rolls' if ROLLS else ''}.png")
    plt.show()

### Graph 11: variance over rolls and batch size
g = 11
if graphs[g]:
    R, B = 300, 300
    grid = [[(r, b) for b in range(1, B + 1)] for r in range(1, R + 1)]
    z = [[var(r, b, False) for r, b in row] for row in grid]
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(*zip(*[zip(*row) for row in grid]), np.array(z),
                    cmap="viridis")
    ax.set_title("Variance over Rolls and Batch Size")
    ax.set_zlabel("Variance")
    plt.ylabel("Batch Size")
    plt.xlabel("Rolls")
    plt.savefig(f"graphs/graph{g:02}.png")
    plt.show()

