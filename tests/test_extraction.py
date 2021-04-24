from Artha import nlp_extraction
from Artha.nlp_extraction import *


def lists_equal(tickers, test_tickers):
    def lower(tick_list): return [i.lower() for i in tick_list]
    return sorted(lower(tickers)) == sorted(lower(test_tickers))


def lists_subset(tickers, test_tickers):
    def lower(tick_list): return [i.lower() for i in tick_list]
    return set(lower(tickers)).issubset(set(lower(test_tickers)))

class TestTickerExtraction:
    def test_1(self):
        test_string = "$BNB funding is still negative. Basically getting paid to buy the USD dip as the BTC pair approaches a new all time high."
        test_tickers = nlp(test_string)._.tickers
        tickers = ["BNB", "USD", "BTC"]

        assert lists_equal(tickers, test_tickers)

    def test_2(self):
        test_string = "Also, memes is an extreme word considering the utility / ecosystem difference between XRP and BNB."
        test_tickers = nlp(test_string)._.tickers
        tickers = ["XRP", "BNB"]

        assert lists_equal(tickers, test_tickers)

    def test_3(self): 
        test_string = "Bitcoin is $1,000 lower than it was yesterday at this time, and alts are all printing higher highs  across the board led by Ethereum.\n\nThis is the moment we've been waiting for.\n\nSalt szn is over. Alt szn is here."
        test_tickers = nlp(test_string)._.tickers

        tickers = ["Bitcoin", "Ethereum"]

        # Salt is included, but seems like a ticker
        assert lists_subset(tickers, test_tickers)

    def test_4(self):
        test_string = "LITECOIN PLEASE ACTUALLY DO SOMETHING THIS TIME, I LOVE LTC"
        test_tickers = nlp(test_string)._.tickers

        tickers = ["Litecoin", "LTC"]

        # love is included tho it isn't a ticker
        assert lists_subset(tickers, test_tickers)

    def test_5(self):
        test_string = "Low sats like HOT, DENT, SRN, etc. are all moving higher, and you don't think $BTT will follow?"
        test_tickers = nlp(test_string)._.tickers

        tickers = ["HOT", "DENT", "SRN", "BTT"]
        assert lists_equal(tickers, test_tickers)

    def test_6(self):
        test_string = '''1443 $KIN

                         Sh*tty price action, but I feel like this is similar to that BTMX trade I had earlier this month that I exited way too early because I lost my patience.

                         I will not make the same mistake twice.

                         I know where this is headed.

                         I will not miss it when it happens. https://t.co/WKeG8eg5UO'''
        test_tickers = nlp(test_string)._.tickers

        tickers = ["KIN", "BTMX"]
        assert lists_equal(tickers, test_tickers)