import pickle
from problib import PATH

DATA_SOURCE = 1  # 0 = initial data, 1 = complete data with character level
OLD_LIST = False # whether to use the old server_diabled_list
# path of the data folder relative to module path
DATA = f"{PATH[0]}/data/{['old', 'complete'][DATA_SOURCE]}"

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

# maps bundles -> List[str] of series
bundle_dict = load_data("bundle_info")

if DATA_SOURCE == 1:
    # maps series -> Dict[total_kak, highest_kak, chars]
    data = load_data("wa_series_info")
    series_dict_wa, series_dict, series_char, char_value = parse_data(data)

    size = {bundle: bundle_dict[bundle]["num_chars"] for bundle in bundle_dict}
    bundle_dict = {b: info["series"] for b, info in bundle_dict.items()}
    # for b in bundle_dict:
    #     assert size[b] == sum(series_dict[s][-1] for s in bundle_dict[b])
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

def character_values(disable_list: list=server_disabled_list) -> list:
    """ Return the character values from a disable_list. """
    seen = set(disable_list)
    chars = set(char for bundle in bundle_dict for series in bundle_dict[bundle]
                for char in series_char[series] if bundle not in seen)
    return [char_value[char] for char in chars]

def random_variable(values: list) -> tuple:
    """ Returns the support set and the pmf of the kakera random variable. """
    X, freq = sorted(set(values)), {}
    for x in values:
        freq[x] = freq.get(x, 0) + 1
    denom = sum(freq.values())
    return X, [freq[x]/denom for x in X]

disable_list = []
disable_list = ['kadokawa future publishing', 'shueisha', 'kodansha', 'shogakukan', 'akita shoten', 'houbunsha', 'virtual youtubers', 'young gangan', 't-rex', 'comic ryu']
if DATA_SOURCE != 0:
    X, p = random_variable(character_values(disable_list))

