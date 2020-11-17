import pickle
from problib import PATH

DATA_SOURCE = 2  # 0 = initial data, 1 = character level data, 2 = complete data
OLD_LIST = False # whether to use the old server_diabled_list
# path of the data folder relative to module path
DATA = f"{PATH[0]}/data/{['old', 'new', 'complete'][DATA_SOURCE]}"

def load_data(fname: str) -> dict:
    """ Loads a pickle file. """
    with open(f"{DATA}/{fname}.p", "rb") as f:
        return pickle.load(f)

def parse_series_data(series_data: dict) -> tuple:
    """ Parse Avik's format into multiple dictionaries. """
    # load old data
    old = f"{PATH[0]}/data/old"
    with open(f"{old}/wa_series_info.p", "rb") as f:
        old_series_wa = pickle.load(f)

    series_dict_wa = {}
    # maps series -> character names and character names -> kakera value
    series_char, char_value = {}, {}
    seen = set()
    for series, info in series_data.items():
        mx, total = info["highest_kak"], info["total_kak"]
        wa, chars = info["num_char"], list(info["chars"].keys())
        series_dict_wa[series] = (mx, total, wa)

        series_char[series] = chars
        for char in chars:
            char_value[char] = int(info["chars"][char][0])
            # assert char not in seen, "overlap between series"
            seen.add(char)
        values = [int(info["chars"][char][0]) for char in chars]

        # data doesn't include $toggledisturbing so copy from old data
        if series in bundle_dict["disturbing imagery"]:
            series_dict_wa[series] = old_series_wa[series]

        assert wa == len(chars), "number characters doesn't match"
        # assert wa >= old_series_wa[series][-1], "lost characters from old data"
        if len(chars) > 0:
            assert mx == max(values), "maximum value doesn't match"
            assert total == sum(values), "total value doesn't match"
    return series_dict_wa, series_char, char_value

# maps bundles -> List[str] of series
bundle_dict = load_data("bundle_info")

if DATA_SOURCE == 2:
    # maps series -> Dict[total_kak, highest_kak, chars]
    series_data = load_data("wa_series_info")
    series_dict_wa, series_char, char_value = parse_series_data(series_data)

    size, series_dict = {}, {}
    with open(f"{DATA}/bundles-list.txt") as f:
        for line in f:
            name, total = line.split()[:-1], line.split()[-1]
            size[" ".join(name)] = int(total[1:-1])
else:
    if DATA_SOURCE == 0:
        # maps series -> Tuple(top_wa_kak, total_wa_kak, total_wa)
        series_dict_wa = load_data("wa_series_info")
    if DATA_SOURCE == 1:
        series_data = load_data("wa_series_info")
        series_dict_wa, series_char, char_value = parse_series_data(series_data)

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
server_disabled = sum(size[b] for b in bundle_dict) if DATA_SOURCE == 2 else \
    sum(series_dict[s][-1] for s in server_seen)
for s in server_seen:
    if len(series_dict) > 0:
        del series_dict[s]
    del series_dict_wa[s]

bundle_list, series_list = list(bundle_dict.keys()), list(series_dict_wa.keys())

