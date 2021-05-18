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
d = df[-250:]

fig = setup_ichi_graph(d, ticker, time_frame, cloud=True, tkc=True)

# fig.update_layout(
#     title='The Great Recession',
#     yaxis_title='AAPL Stock',
#     shapes = [dict(
#         x0='2016-12-09', x1='2016-12-09', y0=0, y1=1, xref='x', yref='paper',
#         line_width=2)],
#     annotations=[dict(
#         x='2016-12-09', y=0.05, xref='x', yref='paper',
#         showarrow=False, xanchor='left', text='Increase Period Begins')]
# )




app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig,
              config=dict(responsive=True))
])

app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter