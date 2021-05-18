import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
# import Artha
from Artha.trading import *


ticker, time_frame = "ETHBTC", "4h"

# klines = get_klines(ticker, time_frame, "01/01/2020 00:00:00")
# df = get_klines_df(klines)

df = load_klines("ETHBTC")


ichimoku(df)
d = df[-550:]

fig = setup_ichi_graph(d, ticker, time_frame, cloud=True, tkc=True)

# fig.update_layout(
#     shapes = [dict(
#         x0='2021-04-25', x1='2021-04-25', y0=0, y1=1, xref='x', yref='paper',
#         line_width=2)],
#     annotations=[dict(
#         x='2021-04-25', y=0.05, xref='x', yref='paper',
#         showarrow=False, xanchor='left', text='Increase Period Begins')]
# )

bull_tks = [d.bull_tk_cross.index[i] for i in range(len(d)) if d.bull_tk_cross.values[i] == 1]
for date_str in bull_tks:
    fig.update_layout(
        shapes=[dict(x0=date_str, x1=date_str, y0=0, y1=1, xref='x', yref='paper',
                line_width=1)],
        annotations=[dict(
            x=date_str, y=0.05, xref='x', yref='paper',
            showarrow=False, xanchor='left', text='Bull TK cross')]
)

# TODO PROPER INDICATORS annotation
# TODO better graph formatting, (fit screen, be able to scroll)
# TODO confluence of ichimoku indicators
# TODO rsi confluence
# TODO volume confluence
# TODO social media confluence

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig,
              config=dict(responsive=True))
])

app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter