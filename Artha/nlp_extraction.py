import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
from spacy.tokens import Doc
import json


ent_lab = ["ORG", "NORP"]

config = {
    # "phrase_matcher_attr": "LOWER",
    # "validate": True,
    "overwrite_ents": True
}

with open("../data/crypto_tickers.json", "r") as w:
    crypto_ticks = json.loads(w.read())

nlp = spacy.load("en_core_web_sm")

ruler = nlp.add_pipe("entity_ruler", config=config)
ruler.from_disk("../data/crypto_patterns.jsonl")

nlp.add_pipe('spacytextblob')


def get_tickers(doc):
    # , 'nft', 'rss', 'pdf', 'agi', 'status'
    ignore = ['ath']
    tickers = [ent.text.strip() for ent in doc.ents if ent.label_ in ent_lab]
    tickers = [tick for tick in tickers if tick.lower() not in ignore]
    count = 0
    while len(tickers) > 0 and len(tickers) > count:
        i = tickers[count]
        if i not in crypto_ticks.keys() and i not in crypto_ticks.values():
            tickers.pop(count)
        else:
            count += 1

    return tickers


Doc.set_extension("tickers", getter=get_tickers)
