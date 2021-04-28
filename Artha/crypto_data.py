from Artha.binance_api.client import Client
import Artha.configs.binance_config as c
from datetime import datetime
import pandas as pd

key = c.apis[0][0]
secret = c.apis[0][1]
client = Client(key, secret)


def date_to_milli(indexes):
    dates = indexes.index.to_pydatetime()
    # print(dates)
    return str(dates[-1].timestamp()*1000), str(dates[0].timestamp()*1000)


def _date_to_twitter(date):
    obj = datetime.fromtimestamp(date/1000.0)
    return "%s/%s/%s %s:%s:%s" % (obj.month, obj.day, obj.year,
                                  obj.hour, obj.minute, obj.second)


def get_klines(asset, interval, oldest, newest=None):
    if newest:
        return client.get_historical_klines(asset, interval, oldest, newest)
    else:
        return client.get_historical_klines(asset, interval, oldest)


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
