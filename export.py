def write_file(fname: str, s: str) -> None:
    """ Writes the string to the filename. """
    tokens = s.split("$")[1:]
    tokens[0] = " ".join(tokens[0].split()[1:])
    with open(fname, "w") as f:
        for line in sorted(tokens):
            f.write(line.strip() + "\n")

with open("out.txt") as f:
    for line in f:
        if "$disable" in line:
            write_file("disable_list.txt", line)
        if "$antidisable" in line:
            write_file("antidisable_list.txt", line)

