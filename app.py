exec(open("start_app.py").read())


# features = [ 'tk_cross', 'kumo_breakout', 'price_kijun_cross', 'senkou_cross', 'chikou_cross']
features = ["bull_tk_cross", "bull_kumo_breakout"]

app = dash.Dash()

app.layout = html.Div([
    html.Div(children=[

        dcc.Checklist(
            id = "features",
            options = [{'label':f, 'value':f} for f in features],
            value = [features[0]],
            labelStyle = {'display':'block'}
        ),

    ], style={'width':'10%'}),

    html.Div(children=[
        dcc.Loading(
            children = [dcc.Graph(
                id = "plot",
                config=dict(responsive=True)
            )],
            type = 'graph'
        )
    ], style={'width':'90%'})
], style={'display':'flex'})




@app.callback(
    Output('plot', 'figure'),
    Input('features', 'value')
)
def update_graph(features):
    fig = setup_ichi_graph(d, ticker, time_frame, cloud=True, lines=True, features=features)
    return fig


app.run_server(debug=True, use_reloader=True)  # Turn off reloader if inside Jupyter
