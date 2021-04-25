import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
from spacy.tokens import Doc
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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


def get_crypto_tickers(doc):
    ignore = ['ath', 'just', 'add', 'pdf', 'band',
              'ramp', 'salt', 'nft', 'rss']

    tickers = [ent.text.strip() for ent in doc.ents if ent.label_ in ent_lab]
    tickers = [tick for tick in tickers if tick not in ignore]

    final_tickers = []
    for cur in tickers:

        if cur in crypto_ticks.values():
            final_tickers.append(cur)

        elif cur.lower() in crypto_ticks.keys():
            final_tickers.append(crypto_ticks[cur.lower()].upper())

    return list(set(final_tickers))


Doc.set_extension("tickers", getter=get_crypto_tickers)
Doc.set_extension("tweet_id", default=False)
Doc.set_extension("tweeted_at", default=False)



def get_polarity(text):
    return analyzer.polarity_scores(text)

def print_polarity(text):
    vs = get_polarity(text)
    print("{:-<65} {}\n\n".format(text, str(vs)))
