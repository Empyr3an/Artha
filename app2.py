import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
exec(open("load_data.py").read())

chart_features = ["price", "volume"]
features = ["vol_spikes"]

app = dash.Dash()

app.layout = html.Div([
    html.Div(children=[
        html.H3(children = "Chart Features"),
        dcc.Checklist(
            id = "chart_features",
            options = [{'label':f.replace("_", " ").capitalize(), 'value':f} for f in chart_features],
            value=["price", "volume"],
            labelStyle = {'display':'block'}
        ),
        html.H3(children = "Specific Callouts"),
        dcc.Checklist(
            id = "features",
            options = [{'label':f.replace("_", " ").capitalize(), 'value':f} for f in features],
            value = ["vol_spikes"],
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
    fig = setup_ichi_graph(df[4200:], ticker, time_frame, chart=chart_features, features=features)
    return fig


app.run_server(debug=True, use_reloader=True)  # Turn off reloader if inside Jupyter
