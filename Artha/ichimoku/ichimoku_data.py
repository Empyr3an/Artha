import ta
import pandas as pd
import numpy as np


def ichimoku_setup(df):
    ichi = ta.trend.IchimokuIndicator(df["High"], df["Low"], df["Close"])
    df["tenkan_sen"] = ichi.ichimoku_conversion_line()
    df["kijun_sen"] = ichi.ichimoku_base_line()
    df["senkou_a"] = ichi.ichimoku_a()
    df["senkou_b"] = ichi.ichimoku_b()
    trimmed = ichi.ichimoku_a()
    trimmed[0:149] = np.nan
    df["senkou_a_trim"] = trimmed

    df["cloud_width"] = df["senkou_a_trim"] - df["senkou_b"]
    df["cloud_top"] = df[["senkou_a_trim", "senkou_b"]].max(axis=1)
    df["cloud_bottom"] = df[["senkou_a_trim", "senkou_b"]].min(axis=1)

    df["chikou_span"] = ichi.ichimoku_chikou()

    df['bull_tk_cross'] = np.where((df['tenkan_sen'].shift(1) <= df['kijun_sen'].shift(1)) &
                                   (df['tenkan_sen'] > df['kijun_sen']), 1, 0)
    df['bear_tk_cross'] = np.where((df['tenkan_sen'].shift(1) >= df['kijun_sen'].shift(1)) &
                                   (df['tenkan_sen'] < df['kijun_sen']), 1, 0)

    # edit so that only significant breakouts are found
    df['bull_kumo_breakout'] = np.where((df["Open"] < df['cloud_top']) &
                                          (df["Close"] > df['cloud_top']), 1, 0)
    df['bear_kumo_breakout'] = np.where((df["Open"] > df['cloud_bottom']) &
                                          (df["Close"] < df['cloud_bottom']), 1, 0)

    kumo_twist = np.zeros(len(df.values))
    for i in range(len(df.values)):
        if df["cloud_width"][i]*df["cloud_width"][i-1] < 0:
            kumo_twist[i] = 1
    df["kumo_twist"] = kumo_twist

    # kumo_diff=df["cloud_width"].shift(1) * df["cloud_width"]

    return df

# def basic_entry(df):

# df['above_cloud']=0
# df['above_cloud']=np.where((df['Low'] > df['senkou_a'])   &
								# (df['Low'] > df['senkou_b'] ), 1, df['above_cloud'])
# df['above_cloud']=np.where((df['High'] < df['senkou_a'])  &
								# (df['High'] < df['senkou_b']), -1, df['above_cloud'])
# df['A_above_B']=np.where((df['senkou_a'] > df['senkou_b']), 1, -1)



# df['price_tenkan_cross']=np.NaN
# df['price_tenkan_cross']=np.where((df['Open'].shift(1) <= df['tenkan_sen'].shift(1))  &
								# (df['Open'] > df['tenkan_sen']), 1, df['price_tenkan_cross'])
# df['price_tenkan_cross']=np.where((df['Open'].shift(1) >= df['tenkan_sen'].shift(1))  &
								# (df['Open'] < df['tenkan_sen']), -1, df['price_tenkan_cross'])



# df['buy']=np.NaN
# df['buy']=np.where((df['above_cloud'].shift(1) == 1)  &
								# (df['A_above_B'].shift(1) == 1) & ((df['tenkan_kiju_cross'].shift(1) == 1) | (df['price_tenkan_cross'].shift(1) == 1)), 1, df['buy'])
# df['buy']=np.where(df['tenkan_kiju_cross'].shift(1) == -1, 0, df['buy'])
# df['buy'].ffill(inplace=True)


# df['sell']=np.NaN
# df['sell']=np.where((df['above_cloud'].shift(1) == -1)  &
								# (df['A_above_B'].shift(1) == -1) & ((df['tenkan_kiju_cross'].shift(1) == -1) | (df['price_tenkan_cross'].shift(1) == -1)), -1, df['sell'])
# df['sell']=np.where(df['tenkan_kiju_cross'].shift(1) == 1, -1, df['sell'])
# df['sell'].ffill(inplace=True)




# df['position']=df['buy'] + df['sell']
# df['stock_returns']=np.log(df['Open']) - np.log(df['Open'].shift(1))
# df['strategy_returns']=df['stock_returns'] * df['position']

# df[['stock_returns','strategy_returns']].cumsum().plot(figsize=(15,8))
