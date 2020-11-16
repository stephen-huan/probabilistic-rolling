import matplotlib.pyplot as plt
import numpy as np
from prob import *
import model

graphs = [None] + [0]*10
graphs[5] = 0
fig = plt.figure(tight_layout=True)

def graph_rv(X: list, p: list, i: int=0, label: str=None) -> None:
    """ Graphs a random variable using a stem plot. """
    plt.stem(X, p, linefmt=f"C{i}-", markerfmt=f"C{i}o", label=label)
    plt.ylabel("Probability")
    plt.xlabel("Value")

### Graph 1: pmf of X
if graphs[1]:
    graph_rv(X, p)
    plt.title("Random Variable X")
    # plt.savefig("graphs/graph1.png")
    plt.show()

### Graph 2: pmf of Zn
if graphs[2]:
    B = 10
    for i, b in enumerate([1, B]):
        graph_rv(Z, [fz(z, b) for z in Z], i, f"Z with batch size {b}")
    plt.title("Random Variable Zs")
    plt.legend()
    # plt.savefig("graphs/graph2.png")
    plt.show()

### Graph 3: pmf of the model 
if graphs[3]:
    R, B = 30, 10
    m = model.Model(R)
    graph_rv(X, p, 0, "X")
    graph_rv(Z, [fz(z) for z in Z], 1, f"Z with batch size {B}")
    graph_rv(X, [m.p_k(x) for x in X], 2, f"Model pmf over {R} rolls")
    plt.title("Random Variable of the Model")
    plt.legend()
    # plt.savefig("graphs/graph3.png")
    plt.show()

### Graph 4: the E[t] dropoff over time
if graphs[4]:
    R, B = 300, 10
    BATCHES = R//B
    x, y = list(range(R + 1)), [Er(0, r) for r in range(R + 1)]
    # xz = [b*B for b in range(BATCHES + 1)]
    # yz = [Er(1, b) for b in range(BATCHES + 1)]
    yf = list(map(Ef, range(R + 1)))
    plt.plot(x, y, label="batch size of 1")
    # plt.plot(xz, yz, label=f"batch size of {B}")
    plt.plot(x, yf, label=f"batch size of {B}")
    plt.title("Expected Value over Time")
    plt.ylabel("Expected Value (kakera)")
    plt.xlabel("Time (rolls)")
    plt.legend()
    # plt.savefig("graphs/graph4.png")
    plt.show()

### Graph 5: the derivative E[t] with respect to t
if graphs[5]:
    R = 30
    x, yf = list(range(R + 1)), list(map(Ef, range(R + 1)))
    yp = [yf[i + 1] - yf[i] for i in range(len(yf) - 1)]
    plt.plot(x[1:], yp)
    plt.title("Change over Time")
    plt.ylabel("Change in Expected Value (kakera)")
    plt.xlabel("Time (rolls)")
    # plt.savefig("graphs/graph5.png")
    plt.show()

### Graph 6: unit price of rolls
if graphs[6]:
    grid = [[(r, k) for k in range(1, 11)] for r in range(R + 1)]
    z = [[price(r, k)/k for r, k in row] for row in grid]
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(*zip(*[zip(*row) for row in grid]), np.array(z),
                    cmap="viridis")
    ax.set_title("Roll Pricing Model")
    ax.set_zlabel("Unit Price of Rolls (Kakera/Roll)")
    ax.set_ylabel("Number of Rolls Sold")
    ax.set_xlabel("Buyer's Number of Rolls")
    # plt.savefig("graphs/graph6.png")
    plt.show()

### Graph 7: variance of the model over rolls
def model_pmf(r: int=R, b: int=B,
        ra: bool=model.ROLLS_AVAILABLE, rc: int=model.ROLLS_CYCLE) -> float:
    """ pmf for the given parameterized model. """
    m = model.Model(r, b, ra, rc)
    return [m.p_k(x) for x in X]

var = lambda *args: Var(model_pmf(*args))

if graphs[7]:
    R, B = 600, 100
    x, y = list(range(R + 1)), [var(r, B) for r in range(R + 1)]
    plt.plot(x, y)
    plt.title("Model Variance over Time")
    plt.ylabel("Variance (kakera^2)")
    plt.xlabel("Rolls")
    plt.savefig("graphs/graph7.png")
    plt.show()

### Graph 8: variance over batch size 
if graphs[8]:
    R = 100
    x, y = list(range(1, B + 1)), [var(R, b) for b in range(1, B + 1)]
    plt.plot(x, y)
    plt.title("Model Variance over Batch Size")
    plt.ylabel("Variance (kakera^2)")
    plt.xlabel("Batch Size")
    plt.savefig("graphs/graph8.png")
    plt.show()

### Graph 9: variance over rolls and batch size
if graphs[9]:
    grid = [[(r, b) for b in range(1, B + 1)] for r in range(1, R + 1)]
    z = [[var(r, b, False) for r, b in row] for row in grid]
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(*zip(*[zip(*row) for row in grid]), np.array(z),
                    cmap="viridis")
    ax.set_title("Variance over Rolls and Batch Size")
    ax.set_zlabel("Variance")
    plt.ylabel("Batch Size")
    plt.xlabel("Rolls")
    plt.savefig("graphs/graph9.png")
    plt.show()

