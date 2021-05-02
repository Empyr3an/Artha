import spacy
from spacy.tokens import Doc
import json
import Artha.data_process as dp
from datetime import datetime
import numpy as np
from collections import Counter
from tqdm import tqdm

# from spacytextblob.spacytextblob import SpacyTextBlob
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# analyzer = SentimentIntensityAnalyzer()

ent_lab = ["ORG", "NORP", "MONEY"]

config = {
    # "phrase_matcher_attr": "LOWER",
    # "validate": True,
    "overwrite_ents": True
}

with open("../data/binance_tickers.json", "r") as w:
    crypto_ticks = json.loads(w.read())

nlp = spacy.load("en_core_web_sm")

ruler = nlp.add_pipe("entity_ruler", config=config, after="ner")
ruler.from_disk("../data/binance_patterns.jsonl")

# nlp.add_pipe('spacytextblob')


def _get_crypto_tickers(doc):
    ignore = ['ath', 'just', 'add', 'pdf', 'band',
              'ramp', 'salt', 'nft', 'rss', 'iq',
              'triggers', 'og', 'win', 'auto']

    tickers = [ent.text.strip() for ent in doc.ents
               if ent.label_ in ent_lab and ent.text.lower() not in ignore]
    # tickers = [tick for tick in tickers if tick not in ignore]

    final_tickers = []
    for cur in tickers:

        if cur in crypto_ticks.values():
            final_tickers.append(cur)

        elif cur.lower() in crypto_ticks.keys():
            final_tickers.append(crypto_ticks[cur.lower()].upper())

    return list(set(final_tickers))


Doc.set_extension("tickers", getter=_get_crypto_tickers)
Doc.set_extension("tweet_id", default=False)
Doc.set_extension("tweeted_at", default=False)
Doc.set_extension("username", default=False)


def run_pipeline(tweet_text):
    docs = []
    with nlp.select_pipes(disable=["tagger", "parser", "lemmatizer"]):
        for doc, context in tqdm(nlp.pipe(tweet_text,
                                          as_tuples=True,
                                          n_process=-1)):

            if doc._.tickers:
                doc._.tweet_id = context["id"]
                doc._.username = context["username"]
                try:
                    doc._.tweeted_at = datetime.strftime(
                        datetime.strptime(context["created_at"],
                                        '%a %b %d %H:%M:%S +0000 %Y'),
                        '%m/%d/%Y %H:%M:%S')
                    docs.append(doc)
                except ValueError:
                    doc._.tweeted_at = datetime.strftime(
                        datetime.strptime(context["created_at"][:-5],
                                        "%Y-%m-%dT%H:%M:%S"),
                        '%m/%d/%Y %H:%M:%S')
                    docs.append(doc)

    return docs


def get_mention_scores(username, docs):
    def expo_func(x): return np.exp(-.07*x)

    all_ticks = Counter([tick for doc in docs
                         for tick in doc._.tickers]).most_common()

    tick_dict = {tick[0]: index for index, tick in enumerate(all_ticks)}

    mentions = np.zeros((len(tick_dict), len(docs)))

    # fill in values of dict lists where ticker is mentioned
    for ind, doc in enumerate(docs):
        for tick in doc._.tickers:
            mentions[tick_dict[tick]][ind] += 1

    # function of array of tweet times
    tweet_times = np.array([dp.time_diff(doc._.tweeted_at) for doc in docs])
    tweet_times = expo_func(tweet_times.reshape((len(docs), 1)))

    # multiply matrix of mentions by time vector
    mul = np.matmul(mentions, tweet_times)\
            .round(5).reshape(1, len(all_ticks))[0]

    # list of edges to add
    return list(zip([username] * len(docs), list(tick_dict.keys()), mul))
