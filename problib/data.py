import pickle, os
from problib import PATH

DATA_SOURCE = 1  # 0 = initial data, 1 = complete data with character level
OLD_LIST = False # whether to use the old server_diabled_list
# path of the data folder relative to module path
DATA = f"{PATH[0]}/data/{['old', 'complete'][DATA_SOURCE]}"

# bundles and series can be disabled, only series can be antidisabled
# limits on the number able to be disabled and antidisabled
# overlap limit is the number of characters able to be disabled total
NUM_DISABLE, OVERLAP, NUM_ANTIDISABLE = 10, 20000, 500
# file paths to read disable and antidisable lists from
DISABLE_LIST, ANTIDISABLE_LIST = "disable_list.txt", "antidisable_list.txt"

def load_data(fname: str) -> dict:
    """ Loads a pickle file. """
    with open(f"{DATA}/{fname}.p", "rb") as f:
        return pickle.load(f)

def parse_data(series_data: dict) -> tuple:
    """ Parse Avik's format into multiple dictionaries. """
    # load old data
    old = f"{PATH[0]}/data/old"
    with open(f"{old}/wa_series_info.p", "rb") as f:
        old_series_wa = pickle.load(f)

    series_dict_wa, series_dict = {}, {}
    # maps series -> character names and character names -> kakera value
    series_char, char_value = {}, {}
    seen = set()
    for series, info in series_data.items():
        mx, total = info["highest_kak"], info["total_kak"]
        wa, chars = info["num_wa"], list(info["chars"].keys())
        values = [int(info["chars"][char][0]) for char in chars]
        series_dict_wa[series] = (max(values + [0]), sum(values), len(values))
        series_dict[series] = (info["num_char"],)

        series_char[series] = chars
        for char in chars:
            char_value[char] = int(info["chars"][char][0])
            assert char not in seen, "overlap between series"
            seen.add(char)

        # data doesn't include $toggledisturbing so copy from old data
        if series in bundle_dict["disturbing imagery"]:
            series_dict_wa[series] = old_series_wa[series]

        assert wa == len(values), "number characters doesn't match"
        # assert wa >= old_series_wa[series][-1], "lost characters from old data"
        if len(chars) > 0:
            # assert mx == max(values), "maximum value doesn't match"
            # assert total == sum(values), "total value doesn't match"
            pass
    return series_dict_wa, series_dict, series_char, char_value

def parse_list(fname: str) -> list:
    """ Reads a text file in Mudae's list format. """
    lines = []
    with open(fname) as f:
        for line in f:
            name, total = line.split()[:-1], line.split()[-1].strip()
            if total[0] + total[-1] == "()":
                name, total = " ".join(name), int(total[1:-1])
            else:
                name = line
            lines.append(name.strip().lower())
    return lines

# maps bundles -> List[str] of series
bundle_dict = load_data("bundle_info")

if DATA_SOURCE == 1:
    size = {bundle: bundle_dict[bundle]["num_chars"] for bundle in bundle_dict}
    bundle_dict = {b: info["series"] for b, info in bundle_dict.items()}
    # for b in bundle_dict:
    #     assert size[b] == sum(series_dict[s][-1] for s in bundle_dict[b])

    # maps series -> Dict[total_kak, highest_kak, chars]
    data = load_data("wa_series_info")
    series_dict_wa, series_dict, series_char, char_value = parse_data(data)
if DATA_SOURCE == 0:
    # maps series -> Tuple(top_wa_kak, total_wa_kak, total_wa)
    series_dict_wa = load_data("wa_series_info")
    # maps series -> Tuple(top_kak, total_kak, total_char)
    series_dict = load_data("total_series_info")
    # compute sizes of each bundle
    # number disabled is irrespective of overlap, counts it twice
    size = {bundle: sum(series_dict[s][-1] for s in series)
            for bundle, series in bundle_dict.items()}

# disable server bundles
server_disabled_list = ["western", "disturbing imagery"]
if OLD_LIST:
    # at some point in time we thought $toggledisturbing toggled horror genre 
    server_disabled_list = ["western", "disturbing imagery", "horror genre"]

server_seen = set(x for b in server_disabled_list for x in bundle_dict[b])
for bundle, series in bundle_dict.items():
    bundle_dict[bundle] = set(s for s in series if s not in server_seen)
server_wa = sum(series_dict_wa[s][-1] for s in server_seen)
server_disabled = sum(series_dict[s][-1] for s in server_seen)
for s in server_seen:
    del series_dict[s]
    del series_dict_wa[s]

bundle_list, series_list = list(bundle_dict.keys()), list(series_dict_wa.keys())

### tie-in to prob

def get_list(fname: str) -> list:
    """ Reads a list from a file. """
    return parse_list(fname) if os.path.exists(fname) else []

def get_series(bundle_list: list) -> set:
    """ Gets the set of series associated with a bundle list. """
    # if a bundle is not in bundle_dict, it's a series and contains only itself
    return set(series for b in bundle_list
               for series in bundle_dict.get(b, [b]))

def character_values(disable_list: list=server_disabled_list,
                     anti_list: list=[]) -> list:
    """ Return the character values from a disable_list. """
    seen = get_series(disable_list)
    series = (set(series_list) - seen) | set(antidisable_list)
    chars = set(char for s in series for char in series_char[s])
    return [char_value[char] for char in chars]

def random_variable(values: list) -> tuple:
    """ Returns the support set and the pmf of the kakera random variable. """
    X, freq = sorted(set(values)), {}
    for x in values:
        freq[x] = freq.get(x, 0) + 1
    denom = sum(freq.values())
    return X, [freq[x]/denom for x in X]

# read user-specific disable and antidisable lists from text files 
disable_list = get_list(DISABLE_LIST)
antidisable_list = get_list(ANTIDISABLE_LIST)
if DATA_SOURCE != 0:
    X, p = random_variable(character_values(disable_list, antidisable_list))

