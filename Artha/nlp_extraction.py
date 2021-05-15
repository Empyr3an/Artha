import spacy
from spacy.tokens import Doc
import json
# import Artha.data_process as dp
from datetime import datetime
# import numpy as np
from tqdm import tqdm
import contractions
from spacy.tokens import DocBin
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


def run_pipeline(tweet_text, save_location="backup.txt"):
    docs = []
    doc_bin = DocBin(attrs=["ENT_IOB", "ENT_TYPE"], store_user_data=True)
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
                except ValueError:  # different tweet format
                    doc._.tweeted_at = datetime.strftime(
                        datetime.strptime(context["created_at"][:-5],
                                          "%Y-%m-%dT%H:%M:%S"),
                        '%m/%d/%Y %H:%M:%S')

                docs.append(doc)
                doc_bin.add(doc)

    with open(save_location, "wb") as f:
        f.write(doc_bin.to_bytes())

    return docs


def load_backup(save_location="backup.txt"):
    with open(save_location, "rb") as f:
        doc_bin = DocBin().from_bytes(f.read())
        print("loaded")
        return list(doc_bin.get_docs(nlp.vocab))


def remove_tags(text):
    if text and text[0] == "@":
        return remove_tags(text.split(" ", 1)[1]) if " " in text else ""
    else:
        return text


def format_tweets(tweets, username):

    tweet_text = []

    text_type = "full_text" if "full_text" in tweets[0].keys() else "text"

    # strips initial tweet mentions to only store text
    for ind, tweet in enumerate(tweets):
        sent = contractions.fix(
                        remove_tags(tweet[text_type])
                        .replace("&amp;", "and")
                        .replace("@", ""))

        if not sent:
            tweets.pop(ind)
        else:
            cleaned_tweet = (sent, {
                        "created_at": tweet["created_at"],
                        "id": tweet["id"],
                        "username": username
                        # "user_mentions": [user["screen_name"]
                        #                   for user in tweet["user_mentions"]]
                        })
            tweet_text.append(cleaned_tweet)
            # returns tuple of (text, {created date, tweet index})
            # TODO uncomment user mentions here if needed
    return tweet_text
