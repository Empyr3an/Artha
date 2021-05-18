import ta
import pandas as pd
import numpy as np
import chart_studio.plotly as py
import plotly.graph_objs as go

import plotly.subplots as ms


def ichimoku(df):
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

    df['bull_tk_cross'] = np.where((df['tenkan_sen'].shift(1) <= df['kijun_sen'].shift(1)) & (df['tenkan_sen'] > df['kijun_sen']), 1, 0)
    df['bear_tk_cross'] = np.where((df['tenkan_sen'].shift(1) >= df['kijun_sen'].shift(1)) & (df['tenkan_sen'] < df['kijun_sen']), 1, 0)

    # edit so that only significant breakouts are found
    df['bull_kumo_pricecross'] = np.where((df["Open"] < df['cloud_top']) & (df["Close"] > df['cloud_top']), 1, 0)
    df['bear_kumo_pricecross'] = np.where((df["Open"] > df['cloud_bottom']) & (df["Close"] < df['cloud_bottom']), 1, 0)

    kumo_twist = np.zeros(len(df.values))
    for i in range(len(df.values)):
        if df["cloud_width"][i]*df["cloud_width"][i-1] < 0:
            kumo_twist[i] = 1
    df["kumo_twist"] = kumo_twist

    # kumo_diff=df["cloud_width"].shift(1) * df["cloud_width"]

    # axs[0].plot(data.index, data.kumo_twist*max(data.Close), label='kumo_twist', color ="blueviolet")


def setup_ichi_graph(d, ticker, time_frame, cloud=True, tkc=True):
    fig = ms.make_subplots(rows=2,
                           cols=1,
                           shared_xaxes=True,
                           vertical_spacing=0.02,
                           row_heights=[.8, .2])

    fig.update_layout(
        title={
            'text': ticker + " "+time_frame,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        yaxis1_title="Price",
        yaxis2_title="Volume",
        xaxis2_title="Time",
        hovermode="x",
        xaxis_rangeslider_visible=False
    )

    # add basic candlesticks
    fig.add_trace(go.Candlestick(
        x=d.index, low=d.Low, high=d.High, close=d.Close, open=d.Open,
        increasing_line_color="green", hovertext=d["Ind"], showlegend=False,
        decreasing_line_color="red"),
        row=1, col=1)

    # add volume
    fig.add_trace(go.Bar(x=d.index,
                         y=d.Volume,
                         marker_color=['royalblue']*len(d),
                         showlegend=False),
                  row=2,
                  col=1)

    # adding cloud and other features

    fig = add_cloud(d, fig) if cloud else fig
    fig = add_tkc(d, fig) if tkc else fig

    return fig


def add_cloud(d, fig):

    fig.add_trace(go.Scatter(x=d['senkou_a'].index,
                             y=d['senkou_a'],
                             type='scatter',
                             mode='lines',
                             line_width=1,
                             marker_color='seagreen',
                             name='senkou_a',
                             hoverinfo='skip'))

    fig.add_trace(go.Scatter(x=d['senkou_a_trim'].index,
                             y=d['senkou_a_trim'],
                             type='scatter',
                             mode='lines',
                             line_width=1,
                             marker_color='seagreen',
                             name='senkou_a_trim',
                             opacity=0,
                             showlegend=False,
                             hoverinfo='skip'))

    fig.add_trace(go.Scatter(x=d['cloud_bottom'].index,
                             y=d['cloud_bottom'],
                             type='scatter',
                             mode='lines',
                             line_width=1,
                             marker_color='seagreen',
                             name='cloud_bottom',
                             opacity=0,
                             showlegend=False,
                             fill="tonexty",
                             hoverinfo='skip'))

    fig.add_trace(go.Scatter(x=d['senkou_b'].index,
                             y=d['senkou_b'],
                             type='scatter',
                             mode='lines',
                             line_width=1,
                             marker_color='red',
                             name='senkou_b',
                             hoverinfo='skip'))

    fig.add_trace(go.Scatter(x=d['cloud_bottom'].index,
                             y=d['cloud_bottom'],
                             type='scatter',
                             mode='lines',
                             line_width=1,
                             marker_color='red',
                             name='cloud_bottom',
                             opacity=0,
                             showlegend=False,
                             fill="tonexty",
                             hoverinfo='skip'))

    return fig


def add_tkc(d, fig):
    fig.add_trace(go.Scatter(x=d['tenkan_sen'].index,
                             y=d['tenkan_sen'],
                             type='scatter',
                             mode='lines',
                             line_width=1,
                             marker_color='dodgerblue',
                             name='tenkan_sen',
                             hoverinfo='skip'))

    fig.add_trace(go.Scatter(x=d['kijun_sen'].index,
                             y=d['kijun_sen'],
                             type='scatter',
                             mode='lines',
                             line_width=1,
                             marker_color='goldenrod',
                             name='kijun_sen',
                             hoverinfo='skip'))

    fig.add_trace(go.Scatter(x=d['chikou_span'].index,
                             y=d['chikou_span'],
                             type='scatter',
                             mode='lines',
                             line_width=1,
                             marker_color='lightblue',
                             name='chikou_span',
                             hoverinfo='skip'))
    
    return fig





# df['above_cloud']=0
# df['above_cloud']=np.where((df['Low'] > df['senkou_a'])  & (df['Low'] > df['senkou_b'] ), 1, df['above_cloud'])
# df['above_cloud']=np.where((df['High'] < df['senkou_a']) & (df['High'] < df['senkou_b']), -1, df['above_cloud'])
# df['A_above_B']=np.where((df['senkou_a'] > df['senkou_b']), 1, -1)



# df['price_tenkan_cross']=np.NaN
# df['price_tenkan_cross']=np.where((df['Open'].shift(1) <= df['tenkan_sen'].shift(1)) & (df['Open'] > df['tenkan_sen']), 1, df['price_tenkan_cross'])
# df['price_tenkan_cross']=np.where((df['Open'].shift(1) >= df['tenkan_sen'].shift(1)) & (df['Open'] < df['tenkan_sen']), -1, df['price_tenkan_cross'])



# df['buy']=np.NaN
# df['buy']=np.where((df['above_cloud'].shift(1) == 1) & (df['A_above_B'].shift(1) == 1) & ((df['tenkan_kiju_cross'].shift(1) == 1) | (df['price_tenkan_cross'].shift(1) == 1)), 1, df['buy'])
# df['buy']=np.where(df['tenkan_kiju_cross'].shift(1) == -1, 0, df['buy'])
# df['buy'].ffill(inplace=True)


# df['sell']=np.NaN
# df['sell']=np.where((df['above_cloud'].shift(1) == -1) & (df['A_above_B'].shift(1) == -1) & ((df['tenkan_kiju_cross'].shift(1) == -1) | (df['price_tenkan_cross'].shift(1) == -1)), -1, df['sell'])
# df['sell']=np.where(df['tenkan_kiju_cross'].shift(1) == 1, -1, df['sell'])
# df['sell'].ffill(inplace=True)




# df['position']=df['buy'] + df['sell']
# df['stock_returns']=np.log(df['Open']) - np.log(df['Open'].shift(1))
# df['strategy_returns']=df['stock_returns'] * df['position']

# df[['stock_returns','strategy_returns']].cumsum().plot(figsize=(15,8))
