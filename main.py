import prob

EXIT = "exit"

def get_input(f, prompt: str):
    """ Runs a function on the input until it is valid. """
    while True:
        try:
            s = input(prompt)
            if "claim" in s.lower():
                return EXIT
            return f(s)
        except ValueError:
            print("Invalid input.")

def render_num(n: int) -> str:
    return str(n) + {1: "st", 2: "nd", 3: "rd"}.get(n, "th")

if __name__ == "__main__":
    while True:
        R = get_input(int, "How many rolls do you have left? Not the number shown \
by $tu, but the total number of rolls until the next claim. \n")
        print(f"Expected value is {prob.Ef(R):.3f}")
        for r in range(R, 0, -1):
            p = R - r + 1
            k = get_input(int, f"Kakera value of the {render_num(p)} roll character? ")
            if k == EXIT:
                break
            # new batch, reset b and i
            if (p - 1) % prob.B == 0:
                b, i = -float("inf"), 0
            if k > b:
                b, i = k, p
            E = prob.Ef(r - 1)
            print(f"Expected value of next rolls is {E:.3f}")
            if b >= E:
                print(f"Since best character value {b} >= {E:.3f}, \
recommend CLAIM character on roll {i}.")

