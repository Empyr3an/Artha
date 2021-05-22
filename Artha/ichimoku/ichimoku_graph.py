
import chart_studio.plotly as py
import plotly.graph_objs as go
import plotly.subplots as ms

def setup_ichi_graph(d, ticker, time_frame, cloud=True, lines=True, tkc=True, pkc=True, kb=True, sc=True, cc=True):
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
        xaxis_rangeslider_visible=False,
        height=950
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
    if cloud:
        fig = add_ichimoku_cloud(d, fig)
    if lines:
        fig = add_tenkan_kijun(d, fig)
    if tkc:
        fig = tenkan_kijun_cross(d, fig)
    if pkc:
        fig = price_kijun_cross(d, fig)
    if kb:
        fig = kumo_breakout(d, fig)
    if sc:
        fig = senkou_cross(d, fig)
    if cc:
        fig = chikou_cross(d, fig)
    return fig

def add_ichimoku_cloud(d, fig):

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

def add_tenkan_kijun(d, fig):
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


def tenkan_kijun_cross(d, fig):
    bull_tks = [d.bull_tk_cross.index[i] for i in range(len(d)) if d.bull_tk_cross.values[i] == 1]
    for date_str in bull_tks:
        fig.update_layout(
            shapes=[dict(x0=date_str, x1=date_str, y0=0, y1=1, xref='x', yref='paper',
                    line_width=1)],
            annotations=[dict(
                x=date_str, y=0.05, xref='x', yref='paper',
                showarrow=False, xanchor='left', text='Bull TK cross')]
    )

# fig.update_layout(
#     shapes = [dict(
#         x0='2021-04-25', x1='2021-04-25', y0=0, y1=1, xref='x', yref='paper',
#         line_width=2)],
#     annotations=[dict(
#         x='2021-04-25', y=0.05, xref='x', yref='paper',
#         showarrow=False, xanchor='left', text='Increase Period Begins')]
# )

    return fig

def price_kijun_cross(d, fig):

    return fig

def kumo_breakout(d, fig):

    return fig

def senkou_cross(d, fig):

    return fig

def chikou_cross(d, fig):

    return fig



# axs[0].plot(data.index, data.kumo_twist*max(data.Close), label='kumo_twist', color ="blueviolet")
