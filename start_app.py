
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from Artha.binance_data import *
from Artha.ichimoku import *
import time

ticker, time_frame = "ETHBTC", "4h"

# klines = get_klines(ticker, time_frame, "01/01/2020 00:00:00")
# df = get_klines_df(klines)

d = ichimoku_setup(load_klines("ETHBTC"))[-550:]

