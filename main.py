from problib import model

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
    R = get_input(int, "How many rolls do you have left? Not the number shown \
by $tu, but the total number of rolls until the next claim. \n")
    rolls_left = get_input(int, "How many $rolls do you have? \n")
    m = model.Model(R)
    m.rolls_left, rolls_used = rolls_left, 0
    print(f"Default parameters:\nRolls left: {m.r}\nBatch size: {m.B}\n\
$rolls allowed: {'yes' if m.ROLLS_AVAILABLE else 'no'}\n\
claim cycles until new $rolls: {m.ROLLS_CYCLE}")
    print(f"\tExpected value is {m.Ef(R):.3f}")

    while m.r > 0:
        p = R - m.r + 1 + rolls_used*m.B
        k = get_input(int, f"Kakera value of the {render_num(p)} roll character? ")
        i = m.update(k)
        print(f"Current batch: {m.l}")
        print(f"\tExpected value of the current batch with best value {m.b}: {m.Eloss(m.r, m.b):.3f}")
        print(f"\tExpected value of the position with {m.r} rolls left: {m.Ef(m.r):.3f}")
        print(f"\tExpected value: {m.status_quo(m.r, m.b):.3f}")
        print(f"\tBuy if someone is selling {m.B} rolls at a price {m.buy():.3f} or less")
        print(f"\tSell if someone is buying at a price {m.sell():.3f} or more")
        if i is not None:
            if i == model.ROLLS:
                print("\t\tUSE $rolls")
                m.rolls_left -= 1
                rolls_used += 1
            else:
                print(f"\t\tCLAIM character {p - (len(m.l) - 1 - i)} worth {m.l[i]}")
                break

