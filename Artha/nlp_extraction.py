import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
import json

config = {
    # "phrase_matcher_attr": "LOWER",
    # "validate": True,
    # "overwrite_ents": True
}
with open("../data/crypto_tickers.json", "r") as w:
    tickers = json.loads(w.read())

nlp = spacy.load("en_core_web_sm")

ruler = nlp.add_pipe("entity_ruler", config=config)
ruler.from_disk("../data/crypto_patterns.jsonl")

nlp.add_pipe('spacytextblob')