import pickle
from problib import PATH

OLD = False      # whether to use old data
OLD_LIST = False # whether to use the old server_diabled_list
# path of the data folder relative to module path
DATA = f"{PATH[0]}/data/{'old' if OLD else 'new'}"

def load_data(fname: str) -> dict:
    """ Loads a pickle file. """
    with open(f"{DATA}/{fname}.p", "rb") as f:
        return pickle.load(f)

# maps bundles -> List[str] of series
bundle_dict = load_data("bundle_info")
if OLD:
    # maps series -> Tuple(top_kak, total_kak, total_char)
    series_dict = load_data("total_series_info")
    # maps series -> Tuple(top_wa_kak, total_wa_kak, total_wa)
    series_dict_wa = load_data("wa_series_info")
else:
    series_dict_wa = load_data("wa_series_info")

# compute sizes of each bundle
# number disabled is irrespective of overlap, counts it twice
size = {bundle: sum(series_dict[s][-1] for s in series)
        for bundle, series in bundle_dict.items()}

# disable server bundles
server_disabled_list = ["Western", "Disturbing Imagery"]
if OLD_LIST:
    # at some point in time we thought $toggledisturbing toggled horror genre 
    server_disabled_list = ["Western", "Horror Genre", "Disturbing Imagery"]

server_seen = set(x for b in server_disabled_list for x in bundle_dict[b])
for bundle, series in bundle_dict.items():
    bundle_dict[bundle] = set(s for s in series if s not in server_seen)
server_wa, server_disabled = map(sum,
zip(*[(series_dict_wa[s][-1], series_dict[s][-1]) for s in server_seen]))
for s in server_seen:
    del series_dict[s]
    del series_dict_wa[s]

bundle_list, series_list = list(bundle_dict.keys()), list(series_dict.keys())

