import matplotlib.pyplot as plt
import numpy as np
from prob import *
import model

graphs = [None, 0, 0, 1, 0, 0, 0]
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
    for i, b in enumerate([1, B]):
        graph_rv(Z, [fz(z, b) for z in Z], i, f"Z with batch size {b}")
    plt.title("Random Variable Zs")
    plt.legend()
    # plt.savefig("graphs/graph2.png")
    plt.show()

### Graph 3: pmf of the model 
m = model.Model(R)
if graphs[3]:
    graph_rv(X, [m.p_k(x) for x in X], 0, f"Model pmf over {R} rolls")
    graph_rv(Z, [fz(z) for z in Z], 1, f"Z with batch size {b}")
    graph_rv(X, p, 2, "X")
    plt.title("Random Variable of the Model")
    plt.legend()
    plt.savefig("graphs/graph3.png")
    plt.show()

### Graph 4: the E[t] dropoff over time
x, y = list(range(R + 1)), [E(0, r) for r in range(R + 1)]
xz = [b*B for b in range(BATCHES + 1)]
yz = [E(1, b) for b in range(BATCHES + 1)]
yf = list(map(Ef, range(R + 1)))
if graphs[4]:
    plt.plot(x, y, label="batch size of 1")
    # plt.plot(xz, yz, label=f"batch size of {b}")
    plt.plot(x, yf, label=f"batch size of {B}")
    plt.title("Expected Value over Time")
    plt.ylabel("Expected Value (kakera)")
    plt.xlabel("Time (rolls)")
    plt.legend()
    # plt.savefig("graphs/graph4.png")
    plt.show()

### Graph 5: the derivative E[t] with respect to t
yp = [yf[i + 1] - yf[i] for i in range(len(y) - 1)]
if graphs[5]:
    plt.plot(x[1:], yp)
    plt.title("Change over Time")
    plt.ylabel("Change in Expected Value (kakera)")
    plt.xlabel("Time (rolls)")
    # plt.savefig("graphs/graph5.png")
    plt.show()

### Graph 6: unit price of rolls
grid = [[(r, k) for k in range(1, 11)] for r in range(R + 1)]
z = [[price(r, k)/k for r, k in row] for row in grid]
if graphs[6]:
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(*zip(*[zip(*row) for row in grid]), np.array(z),
                    cmap="viridis")
    ax.set_title("Roll Pricing Model")
    ax.set_zlabel("Unit Price of Rolls (Kakera/Roll)")
    ax.set_ylabel("Number of Rolls Sold")
    ax.set_xlabel("Buyer's Number of Rolls")
    # plt.savefig("graphs/graph6.png")
    plt.show()

