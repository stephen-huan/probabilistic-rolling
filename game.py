import random
from problib import model
from problib.test_model import sample

def get_input(prompt: str):
    """ Prompts the user until their response is vaild.  """
    while True:
        try:
            s = input(prompt)
            if len(s) == 0:
                return
            i = int(s)
            i = i if i == model.ROLLS else i - 1
            if (i == model.ROLLS and m.rolls_left > 0) or 0 <= i < len(m.l):
                return i
        except ValueError:
            print("Invalid input.")
        else:
            if i == model.ROLLS:
                print("No $rolls available.")
            else:
                print("Not a valid index.")

if __name__ == "__main__":
    random.seed(None)
    game, total = 0, 0
    m = model.Model(ROLLS_AVAILABLE=False)
    m.rolls_left = 0
    print("Type a number to claim that character and -1 to use $rolls. Hit enter to roll again.")
    while True:
        m.reset()
        print(f"\tStarting game #{game + 1}")
        if model.ROLLS_AVAILABLE and game % model.ROLLS_CYCLE == 0:
            m.rolls_left += 1
            print(f"\tGained a use of $rolls. Number in stock: {m.rolls_left}")
        rolls_used, value = 0, 0
        b = 0
        while m.r > 0:
            k = sample()
            m.update(k)
            if len(m.l) == 1:
                b += 1
            s = get_input(f"Batch {b}, roll {len(m.l):2}: Rolled a character with kakera value {k}. ")
            if s is not None:
                if s == model.ROLLS:
                    m._Model__rolls()
                    m.rolls_left -= 1
                    print(f"\tUsing $rolls. Number in stock: {m.rolls_left}")
                else:
                    value = m.l[s]
                    total += value
                    print(f"\tClaimed character {s + 1}, with kakera value {value}.")
                    break
        game += 1
        print(f"\tGame over. Value of {value}")
        print(f"\tRunning average over all games: {total/game:.3f}")

