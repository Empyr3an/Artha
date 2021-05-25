import ta
import pandas as pd
import numpy as np


def ichimoku_setup(df, window=30):
    ichi = ta.trend.IchimokuIndicator(df["High"], df["Low"], df["Close"])
    df["tenkan_sen"] = ichi.ichimoku_conversion_line()
    df["kijun_sen"] = ichi.ichimoku_base_line()
    df["senkou_a"] = ichi.ichimoku_a()
    df["senkou_b"] = ichi.ichimoku_b()
    trimmed = ichi.ichimoku_a()
    trimmed[0:149] = np.nan
    df["senkou_a_trim"] = trimmed

    df["kumo_top"] = df[["senkou_a_trim", "senkou_b"]].max(axis=1)
    df["kumo_bottom"] = df[["senkou_a_trim", "senkou_b"]].min(axis=1)

    df["chikou_span"] = ichi.ichimoku_chikou()

    # Init special features
    df["strong_chikou"] = find_strong_chikous(df)
    # df["strong_tk"] = get

    df['bull_tk_cross'] = np.where((df['tenkan_sen'].shift(1) <= df['kijun_sen'].shift(1)) &
                                   (df['tenkan_sen'] > df['kijun_sen']), 1, 0)
    df['bear_tk_cross'] = np.where((df['tenkan_sen'].shift(1) >= df['kijun_sen'].shift(1)) &
                                   (df['tenkan_sen'] < df['kijun_sen']), 1, 0)

    # edit so that only significant breakouts are found
    df['bull_kumo_breakout'] = np.where((df["Open"] < df['kumo_top']) &
                                          (df["Close"] > df['kumo_top']), 1, 0)
    df['bear_kumo_breakout'] = np.where((df["Open"] > df['kumo_bottom']) &
                                          (df["Close"] < df['kumo_bottom']), 1, 0)


    df["kumo_width"] = df["senkou_a_trim"] - df["senkou_b"]
    kumo_twist = np.zeros(len(df.values))
    for i in range(len(df.values)):
        if df["kumo_width"][i]*df["kumo_width"][i-1] < 0:
            kumo_twist[i] = 1
    # df["kumo_future"] = np.roll(
    df["kumo_twist"] = kumo_twist

    # kumo_diff=df["kumo_width"].shift(1) * df["kumo_width"]

    return df

def find_strong_chikous(df, window=30, pct=5, days=10):
    return np.roll(np.array([is_strong_chikou(df, i) for i in range(len(df.values))]),0)

def in_cloud(val, kline):
    return True if val<kline.kumo_top and val>kline.kumo_bottom else False

def is_strong_chikou(df, index, window=30, pct=5, days=10):
    above = lambda cur_val, candle: True if cur_val*(1+pct/100) < candle[0] else False
    below = lambda cur_val, candle: True if cur_val*(1-pct/100) > candle[1] else False

    cur_chikou = df["chikou_span"].iloc[index-window]
    if np.isnan(cur_chikou):
        return 0

    # pos = df.index.get_indexer_for((df[df.Ind == index-window].index))[0]
    chikou_ranges = df.iloc[index-window:index-window+days]
    [["Low", "High"]]

    for row in chikou_ranges.itertuples():
        if np.isnan(np.sum(row.Low+row.High)):
            return 0
        if in_cloud(cur_chikou, row):
            return 0
        if not(cur_chikou*(1+pct/100) < row.Low or cur_chikou*(1-pct/100)>row.High):
            return 0
    return 1

def percent_diff(current, prev):
    return abs((current-prev)/prev)

# def basic_bull_entry(df):
    # price above kumo
    # tenkan greater than kijun
    # strong chikou
    # 50 pips to next major support
    # bullish future kumo
    # entry less than 2% from tenkan
    # entry less than 3% from kijun
    # entry buffers = .4%?
    # all ichi indicators bullish

    # exit if
    # price greater than 2% from, exit if TS is flat
    # profit greater than 3%, use TS with buffer as stop
    # exit buffer is .4%
    # or just use trailing stop

#     price_above_kumo = np.where(df["Close"] > df["kumo_top"])
# tenkan_above_kijun = np.where(df["tenkan_sen"] > df["kijun_sen"])
# p>

# df['above_kumo']=0
# df['above_kumo']=np.where((df['Low'] > df['senkou_a'])   &
								# (df['Low'] > df['senkou_b'] ), 1, df['above_kumo'])
# df['above_kumo']=np.where((df['High'] < df['senkou_a'])  &
								# (df['High'] < df['senkou_b']), -1, df['above_kumo'])
# df['A_above_B']=np.where((df['senkou_a'] > df['senkou_b']), 1, -1)



# df['price_tenkan_cross']=np.NaN
# df['price_tenkan_cross']=np.where((df['Open'].shift(1) <= df['tenkan_sen'].shift(1))  &
								# (df['Open'] > df['tenkan_sen']), 1, df['price_tenkan_cross'])
# df['price_tenkan_cross']=np.where((df['Open'].shift(1) >= df['tenkan_sen'].shift(1))  &
								# (df['Open'] < df['tenkan_sen']), -1, df['price_tenkan_cross'])



# df['buy']=np.NaN
# df['buy']=np.where((df['above_kumo'].shift(1) == 1)  &
								# (df['A_above_B'].shift(1) == 1) & ((df['tenkan_kiju_cross'].shift(1) == 1) | (df['price_tenkan_cross'].shift(1) == 1)), 1, df['buy'])
# df['buy']=np.where(df['tenkan_kiju_cross'].shift(1) == -1, 0, df['buy'])
# df['buy'].ffill(inplace=True)


# df['sell']=np.NaN
# df['sell']=np.where((df['above_kumo'].shift(1) == -1)  &
								# (df['A_above_B'].shift(1) == -1) & ((df['tenkan_kiju_cross'].shift(1) == -1) | (df['price_tenkan_cross'].shift(1) == -1)), -1, df['sell'])
# df['sell']=np.where(df['tenkan_kiju_cross'].shift(1) == 1, -1, df['sell'])
# df['sell'].ffill(inplace=True)




# df['position']=df['buy'] + df['sell']
# df['stock_returns']=np.log(df['Open']) - np.log(df['Open'].shift(1))
# df['strategy_returns']=df['stock_returns'] * df['position']

# df[['stock_returns','strategy_returns']].cumsum().plot(figsize=(15,8))
