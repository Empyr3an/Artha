import chart_studio.plotly as py
import plotly.graph_objs as go
import plotly.subplots as ms

def setup_ichi_graph(d, ticker, time_frame, kumo=True, lines=True, features=None):
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
        hovermode="x unified",
        height=950,
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

    # adding kumo and other features
    if kumo:
        fig = add_ichimoku_kumo(d, fig)
    if lines:
        fig = add_tenkan_kijun(d, fig)

    fig = add_feature(d, fig, features)

    return fig

def add_ichimoku_kumo(d, fig):

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

    fig.add_trace(go.Scatter(x=d['kumo_bottom'].index,
                             y=d['kumo_bottom'],
                             type='scatter',
                             mode='lines',
                             line_width=1,
                             marker_color='seagreen',
                             name='kumo_bottom',
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

    fig.add_trace(go.Scatter(x=d['kumo_bottom'].index,
                             y=d['kumo_bottom'],
                             type='scatter',
                             mode='lines',
                             line_width=1,
                             marker_color='red',
                             name='kumo_bottom',
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


def add_feature(d, fig, features):
    shapes, annotations = [], []
    for feature in features:

        events = [d[feature].index[i] for i in range(len(d)) if d[feature].values[i] == 1]

        shapes.extend([dict(x0=str(date_str), x1=str(date_str), y0=.22, y1=1, xref='x', yref='paper', line_width=1) for date_str in events])
        annotations.extend([dict(
            x=str(date_str), y=0.22, xref='x', yref='paper',
            showarrow=False, xanchor='left', text=feature.replace("_", " ").capitalize()) for date_str in events])

        #bear tk cross
    fig.update_layout(
        shapes = shapes,
        annotations = annotations
    )
    return fig
