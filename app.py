exec(open("start_app.py").read())

chart_features = ["price", "volume", "kumo", "tenkan", "kijun", "chikou"]
# features = [ 'tk_cross', 'kumo_breakout', 'price_kijun_cross', 'senkou_cross', 'chikou_cross']
# features = ["bull_tk_cross", "bull_kumo_breakout", "strong_chikou"]
features = ["strong_chikou", "strong_tk"]

app = dash.Dash()

app.layout = html.Div([
    html.Div(children=[
        html.H3(children = "Chart Features"),
        dcc.Checklist(
            id = "chart_features",
            options = [{'label':f.replace("_", " ").capitalize(), 'value':f} for f in chart_features],
            value=["price", "volume", "tenkan"],
            labelStyle = {'display':'block'}
        ),
        html.H3(children = "Specific Callouts"),
        dcc.Checklist(
            id = "features",
            options = [{'label':f.replace("_", " ").capitalize(), 'value':f} for f in features],
            # value = [features[0]],
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
    Input('features', 'value'),
    Input('chart_features', 'value')
)
def update_graph(features, chart_features):
    fig = setup_ichi_graph(df[:400], ticker, time_frame, chart=chart_features, features=features)
    return fig


app.run_server(debug=True, use_reloader=True)  # Turn off reloader if inside Jupyter
