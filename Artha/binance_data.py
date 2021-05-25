from binance import AsyncClient, BinanceSocketManager, Client
import Artha.configs.binance_config as c
from datetime import datetime
import pandas as pd
import numpy as np
import concurrent.futures
import os


key = c.apis[0][0]
secret = c.apis[0][1]
client = Client(key, secret)

base3_markets = ["BTC", "BNB", 'ETH', 'TRX', 'XRP'] + \
                ['AUD', 'BRL', 'EUR', 'GBP', 'RUB',
                 'TRY', 'PAX', 'DAI', 'UAH', 'NBN', 'VAI']
base4_markets = ['USDT', 'USDC', 'BUSD', 'IDRT', 'BIDR', 'BVND', 'TUSD']


def date_to_twitter(date):
    obj = datetime.fromtimestamp(date/1000.0)
    return "%s/%s/%s %s:%s:%s" % (obj.month, obj.day, obj.year,
                                  obj.hour, obj.minute, obj.second)


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


def vol_spikes(arr, window=2):
    arr = np.array(arr)
    spikes = []
    for i in range(len(arr)-window-1):
        if np.mean(arr[i:i+window])*5 < arr[i+window+1]:
            spikes.append(i+window+1)
    # print(spikes)
    return spikes


def get_klines(asset, interval, oldest, newest=None):
    if newest:
        klines = client.get_historical_klines(asset, interval, oldest, newest)
    else:
        klines = client.get_historical_klines(asset, interval, oldest)

    return [np.array([float(num) for num in kline]) for kline in klines]


def get_klines_df(klines, window4=30):
    def extra_time(klines): return window4*(klines[-1][0] - klines[-2][0])

    columns = ["Open Time", "Open", "High", "Low", "Close", "Volume",
               "Close Time", "Quote Asset Volume", "Number of Trades",
               "Taker Buy Base Volume", "Taker Buy Quote Asset Volume",
               "Ignore"]

    df = pd.DataFrame.from_records(
                [np.full(len(columns), np.nan)]*window4+
                klines +
                [np.full(len(columns), np.nan)]*window4,
                index=pd.date_range(
                    start=date_to_twitter(klines[0][0]-extra_time(klines)),
                    end=date_to_twitter(klines[-1][0]+extra_time(klines)),
                periods=len(klines)+2*window4),
                columns=columns)

    df["Ind"] = list(range(len(df.index)))
    return df[["Ind"]+columns]


def save_klines(df, ticker):
    df.to_csv("../data/crypto_price_data/"+ticker+".csv", index=True)
    print("saved", ticker)


def klines_worker(ticker, start_date):
    klines = get_klines(ticker, "1h", start_date)
    df = get_klines_df(klines)
    save_klines(df, ticker)
    df.to_csv("../data/crypto_price_data/"+ticker+".csv", index=True)
    return "done "+ticker


def concurrent_download_klines(all_ticks, start_date):
    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
        result = [executor.submit(klines_worker, ticker, start_date) for ticker in all_ticks]
    for future in concurrent.futures.as_completed(result):
        print(future.result())


def load_klines(ticker, location="data/crypto_price_data/"):
    if ticker+".csv" in os.listdir(location):
        df = pd.read_csv(location+ticker+".csv")
        df['Date'] = pd.to_datetime(df['Unnamed: 0'])
        df = df.set_index("Date").drop(['Unnamed: 0'], axis=1)
        return df
    else:
        print("not a valid ticker")
