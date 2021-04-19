import string
import collections
import json
import contractions

with open("../data/crypto_tickers.json", "r") as w:
    tickers = json.loads(w.read())

# ignore the following tickers
too_common_tickers = ["ONE",
                      "IQ",
                      "FOR",
                      "TRY",
                      "WIN",
                      "HOT",
                      "NEAR",
                      "CAN",
                      "HARD",
                      "BULL",
                      "SKY",
                      "FUN",
                      "EASY",
                      "GO",
                      "ADD",
                      "OG",
                      "DATA",
                      "ATM",
                      "ANT",
                      "KEY"]

# ignore the following names
too_common_names = ["JUST", "HONEST", "VERGE"]

for i in too_common_tickers:
    del tickers[i]
for i in too_common_names:
    for k, v in tickers.items():
        if v == i:
            del tickers[k]
            break
# final lists to keep, capitalizes all tickers and names
coin_ticks = [tick.upper() for tick in tickers.keys()]
coin_names = [name.upper() for name in tickers.values()]


def normalize_sentence(sen):
    return contractions.fix(sen).replace("'s", "").replace("\n", " ")\
           .translate(str.maketrans('', '', string.punctuation))\
           .upper()


def extract_crypto_tickers(sentence):
    sen_words = normalize_sentence(sentence).split()
    tickers = [word for word in sen_words if word in coin_ticks]

    return collections.Counter(tickers)


def extract_crypto_names(sentence):

    sentence = " " + normalize_sentence(sentence) + " "
    tickers = [coin for coin in coin_names if " "+coin+" " in sentence]
    return collections.Counter(tickers)


def extract_cashtags(sentence):
    sen_words = normalize_sentence(sentence).split()
    symbols = [word for word in sen_words
               if len(word) > 1 and
               word[0] == "$" and word[1:].isalpha()]

    return collections.Counter(symbols)
