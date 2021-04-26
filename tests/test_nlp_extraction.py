from Artha.nlp_extraction import *
import pytest


def lists_equal(tickers, test_tickers):
    def lower(tick_list): return [i.lower() for i in tick_list]
    return sorted(lower(tickers)) == sorted(lower(test_tickers))

@pytest.mark.parametrize("test_string,real_tickers", [
    ("Will send us into a whirlwind and a lot of tensions between countries will ramp up.", []),
    ("$BNB funding is still negative. Basically getting paid to buy the USD dip as the BTC pair approaches a new all time high.", ["BNB", "USD", "BTC"]),
    ("Also, memes is an extreme word considering the utility / ecosystem difference between XRP and BNB.", ["XRP", "BNB"]),
    ("Bitcoin is $1,000 lower than it was yesterday at this time, and alts are all printing higher highs across the board led by Ethereum.\n\nThis is the moment we've been waiting for.\n\nSalt szn is over. Alt szn is here.", ["BTC", "SALT", "ETH"]), # TODO salt should not be included
    ("LITECOIN PLEASE ACTUALLY DO SOMETHING THIS TIME, I LOVE LTC", ["LTC"]), # Love must not be a ticker
    ("Low sats like HOT, DENT, SRN, etc. are all moving higher, and you don't think $BTT will follow?", ["HOT", "DENT", "BTT"]), #srn not on binance
    ("Bitcoin looks exhausted on weekly. 44k looks like it could be hit. Middle BB band is key, we close below band, 33k is next weekly support.", ["BTC"]), #"BTC"
    ("FSLR volume really starting to come in. I will probably add to some OTM leaps for $FSLR tomorrow. Nice volume came in on Friday Daily as well.", []),
    ("Give me the signal on a good pullback on daily time frame and I will throw extra cash into crypto just for VET", ["VET"]),
    ("Going to use some leverage and add $XRP here.", ["XRP"]),
    ("I really should have traded some $doge for $ENJ at 0.06 cents when I was debating it", ["ENJ"]),
    ("SPACs are just another way to raise money quick. Much like IPOs during the dot com bubble. Big bubble, bigger pop", []),
    ("Same, it is for the most part impossible, certain events can be predicted with higher hit rate than others. Life is just a gamble of probabilities.", []),
    ('''$KIN
        Sh*tty price action, but I feel like this is similar to that BTMX trade I had earlier this month that I exited way too early because I lost my patience.
        I will not make the same mistake twice.
        I know where this is headed.
        I will not miss it when it happens. https://t.co/WKeG8eg5UO''', [])
])
def test_ticker_extraction(test_string, real_tickers):
    test_tickers = nlp(test_string)._.tickers
    assert lists_equal(test_tickers, real_tickers)
