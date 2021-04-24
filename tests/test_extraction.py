from Artha import nlp_extraction
from Artha.nlp_extraction import *

labels = ["ORG", "MONEY", "NORP"]


def lists_equal(correct, doc):
    return sorted(correct) == sorted(get_doc_ents(doc))


def lists_subset(correct, doc):
    set(correct).issubset(get_doc_ents(doc))


def get_doc_ents(doc):
    return [ent.text.strip()
            for ent in doc.ents
            if ent.label_ in labels]


def test_ticker_extraction():
    test_string = """$BNB funding is still negative. Basically
                     getting paid to buy the USD dip as the BTC
                     pair approaches a new all time high."""

    tickers = ["BNB", "USD", "BTC"]

    assert lists_equal(tickers, nlp(test_string))
