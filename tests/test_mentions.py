import pytest
from Artha.mentions import *
from Artha.nlp_extraction import *


def test_get_mention_edges():
    docs = load_backup()
    doc_dict = {}
    for doc in docs:
        if doc._.username not in doc_dict.keys():
            doc_dict[doc._.username] = [doc]
        else:
            doc_dict[doc._.username].append(doc)

    date = "04/03/2021 00:00:00"
    all_mentions = []
    selected_people = ["BTC_JackSparrow", "razoreth", "Nostranomist", "CryptoKaleo", "nebraskangooner", "Rager", "SavageBTC"]
    for username in selected_people:
        cur_mentions = get_mention_edges(doc_dict[username],
                                         username,
                                         follow_weight=.5,
                                         win_start_date=date)
        all_mentions.extend(cur_mentions)
    s = 0
    for i in all_mentions:
        if i[0] == "BTC_JackSparrow":
            # print(i)
            s += i[2]
    assert round(s, 1) == .5


# future integration testing
# s = 0
# rels = neo.get_relations()
# for r in rels:
#     if r._start_node["username"] == "Rager":
#         # print(r.type, r["weight"], r.end_node["ticker"])
#         s+=float(r["weight"])

# print("mentions+follows", s)