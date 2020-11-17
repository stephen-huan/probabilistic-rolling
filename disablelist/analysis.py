# written by Luke Thistlethwaite
import pickle
import random
with open('data/bundle_info.p', 'rb') as f:
    bundle_dict = pickle.load(f) #maps bundles -> List[str] of series
with open('data/total_series_info.p', 'rb') as f:
    series_dict = pickle.load(f) #maps series -> Tuple(top_kak, total_kak, total_char)
with open('data/wa_series_info.p', 'rb') as f:
    wa_series_dict = pickle.load(f) #maps series -> Tuple(top_wa_kak, total_wa_kak, total_wa)

bundle_list = list(bundle_dict.keys())

#$togglewestern and horror settings on the server disable these three bundles by default:
server_disabled_list = ["Western", "Horror Genre", "Disturbing Imagery"]
for b in server_disabled_list:
    bundle_list.remove(b)

#calculate how many waifus are disabled as a result of this
server_disabled_series = set()
for b in server_disabled_list:
    for s in bundle_dict[b]:
        server_disabled_series.add(s)
server_disabled_wa = 0
for s in server_disabled_series:
    top_kak, _, wa_chars = wa_series_dict[s]
    server_disabled_wa += wa_chars
print("Waifus disabled according to server settings:", server_disabled_wa)

#Function that takes in a list of bundles and determines how many waifus are disabled as well as overlap
def calc_disabled(bundles, flag=False):
    """returns tuple (disabled_count, num_wa_disabled)"""
    disabled_series = set()
    disabled_count = 0
    unique_wa = 0
    anti_disable = 0
    for b in bundles:
        for s in bundle_dict[b]: #for each series in the bundle
            _, _, num_char = series_dict[s] #get number of character in series
            disabled_count += num_char #add to overlap counter
            if s not in disabled_series and s not in server_disabled_series: #if the series isn't already disabled, it means the waifus are new
                disabled_series.add(s) #add to disable list
                top_kak, _, wa_chars = wa_series_dict[s] #find out top value of waifu
                if top_kak > 83:
                    anti_disable += 1 #waifu should be anti_disabled if worth stuff
                else:
                    unique_wa += wa_chars #otherwise it'll be disabled, add to list of unique disabled waifus
    if flag:
        return (disabled_count, unique_wa, anti_disable)
    return (disabled_count, unique_wa)

#randomly add a bundle to the bundle set
def add_random(all_bundles, bundle_set):
    addition = random.choice(all_bundles)
    while addition in bundle_set:
        addition = random.choice(all_bundles)
    bundle_set.add(addition)

#yikes lol
def generate_combo(all_bundles):
    my_bundle_set = set()
    while len(my_bundle_set) < 10:
        new_set = my_bundle_set.copy()
        add_random(all_bundles, new_set)
        disabled_count, unique_wa = calc_disabled(list(new_set))
        if disabled_count <= 20000:
            my_bundle_set = new_set
        else:
            return my_bundle_set
    return my_bundle_set



# test = ['Manga Time Kirara', 'Comp Ace', 'Gangan Comics', 'Kodansha', 'Kadokawa Future Publishing', 'Adult Swim', 'A-1 Pictures', 'Webcomics']
# all_disabled_series = set()
# for b in test:
#     for s in bundle_dict[b]:
#         all_disabled_series.add(s)
# for b in pre_list:
#     for s in bundle_dict[b]:
#         all_disabled_series.add(s)

# disabled_waifus = 0
# for s in all_disabled_series:
#     top_kak, total_kak, num_char = wa_series_dict[s]
#     disabled_waifus += num_char

# print(disabled_waifus)
# print(calc_disabled(test, True))
#print(calc_disabled(["Western", "Horror Genre", "Disturbing Imagery"]))

best_set = generate_combo(bundle_list)
_, wa_best = calc_disabled(list(best_set))
for x in range(20000):
    new_set = generate_combo(bundle_list)
    _, wa_score = calc_disabled(list(new_set))
    if wa_score > wa_best:
        wa_best = wa_score
        best_set = new_set
        print(wa_best, best_set)
