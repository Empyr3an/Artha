import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
from spacy.tokens import Doc
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import Artha.data_process as dp
from datetime import datetime

analyzer = SentimentIntensityAnalyzer()

ent_lab = ["ORG", "NORP", "MONEY"]

config = {
    # "phrase_matcher_attr": "LOWER",
    # "validate": True,
    "overwrite_ents": True
}

with open("../data/binance_tickers.json", "r") as w:
    crypto_ticks = json.loads(w.read())

nlp = spacy.load("en_core_web_sm")

ruler = nlp.add_pipe("entity_ruler", config=config)
ruler.from_disk("../data/binance_patterns.jsonl")

nlp.add_pipe('spacytextblob')


def _get_crypto_tickers(doc):
    ignore = ['ath', 'just', 'add', 'pdf', 'band',
              'ramp', 'salt', 'nft', 'rss', 'iq',
              'triggers', 'og', 'win', 'auto']

    tickers = [ent.text.strip() for ent in doc.ents if ent.label_ in ent_lab and ent.text.lower() not in ignore]
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


def run_pipeline(username):
    tweets = dp.load_tweets(username)
    tweet_text = dp.clean_tweets(tweets)

    docs = []
    for doc, context in nlp.pipe(tweet_text, as_tuples=True, n_process=-1): # need to disable pipes to run faster

        doc._.tweet_id = context["id"]
        doc._.tweeted_at = datetime.strftime(datetime.strptime(context["created_at"],'%a %b %d %H:%M:%S +0000 %Y'), '%m/%d/%Y %H:%M:%S')
        docs.append(doc)

    return docs


# def get_polarity(text):
#     return analyzer.polarity_scores(text)

# def print_polarity(text):
#     vs = get_polarity(text)
#     print("{:-<65} {}\n\n".format(text, str(vs)))
