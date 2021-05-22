exec(open("start_app.py").read())

fig = setup_ichi_graph(d, ticker, time_frame, cloud=True, lines=True, tkc=True, pkc=True, kb=True, sc=True, cc=True)
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

app.run_server(debug=True, use_reloader=True)  # Turn off reloader if inside Jupyter
