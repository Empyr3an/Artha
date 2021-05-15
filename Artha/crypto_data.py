from binance import AsyncClient, BinanceSocketManager, Client
import Artha.configs.binance_config as c
from datetime import datetime
import pandas as pd

key = c.apis[0][0]
secret = c.apis[0][1]
client = Client(key, secret)

base3_markets = ["BTC", "BNB", 'ETH', 'TRX', 'XRP'] + \
                ['AUD', 'BRL', 'EUR', 'GBP', 'RUB',
                 'TRY', 'PAX', 'DAI', 'UAH', 'NBN', 'VAI']
base4_markets = ['USDT', 'USDC', 'BUSD', 'IDRT', 'BIDR', 'BVND', 'TUSD']


def _date_to_twitter(date):
    obj = datetime.fromtimestamp(date/1000.0)
    return "%s/%s/%s %s:%s:%s" % (obj.month, obj.day, obj.year,
                                  obj.hour, obj.minute, obj.second)


def get_klines(asset, interval, oldest, newest=None):
    if newest:
        return client.get_historical_klines(asset, interval, oldest, newest)
    else:
        return client.get_historical_klines(asset, interval, oldest)


# def get_klines_df(asset, interval, oldest, newest=None):
    # klines = get_klines(asset, interval, oldest, newest)
def get_klines_df(klines):
    columns = ["Open Time", "Open", "High", "Low", "Close", "Volume",
               "Close Time", "Quote Asset Volume", "Number of Trades",
               "Taker Buy Base Volume", "Taker Buy Quote Asset Volume",
               "Ignore"]

    return pd.DataFrame.from_records(
                klines,
                index=pd.date_range(start=_date_to_twitter(klines[0][0]),
                                    end=_date_to_twitter(klines[-1][0]),
                                    periods=len(klines)),
                columns=columns)


# get dict of quote asset and all base pairs
# {BTC: ["ETH", "LTC", "BNB" ]} etc
def get_quote_dict():
    all_tickers = client.get_ticker()
    all_ticker_symbols = [i["symbol"] for i in all_tickers]
    markets = {}

    for base in base3_markets:
        markets[base] = [i[:-3] for i in all_ticker_symbols if i[-3:] == base]

    for base in base4_markets:
        markets[base] = [i[:-4] for i in all_ticker_symbols if i[-4:] == base]
    return markets


# Inverted dict of markets for each crypto where crypto is base pair
# {"ETH": 'markets': ["BTC", "AUD", "USDC"]} etc
def get_base_dict():
    d = get_quote_dict()
    inverse = dict()
    for key in d:
        # Go through the list that is saved in the dict:
        for item in d[key]:
            # Check if in the inverted dict the key exists
            if item not in inverse:
                # If not create a new list
                inverse[item] = {}
                inverse[item]["markets"] = [key]
            else:
                inverse[item]["markets"].append(key)
    return inverse
