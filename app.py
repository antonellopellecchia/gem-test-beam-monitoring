import datetime
import yaml
import pandas as pd
import argparse

import dash
from dash import dcc
from dash import html
import plotly
from dash.dependencies import Input, Output

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

parser = argparse.ArgumentParser()
parser.add_argument('config', help='configuration file path')
args = parser.parse_args()

with open(args.config, 'r') as config_stream:
    config = yaml.safe_load(config_stream)["monitoring"]
x_column = config["data_x"]
y_columns = config["data_y"]

div_graphs = list()
callback_outputs = list()
for name,y_column in y_columns.items():
    div_graphs.append(html.Div(name))
    div_graphs.append(dcc.Graph(id=f"{y_column}-graph"))
    callback_outputs.append(Output(f"{y_column}-graph", "figure"))
div_graphs.append(dcc.Interval(
    id="interval-component",
    interval=config["sleep_time"]*1000,
    n_intervals=0
    ))

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(html.Div(div_graphs))

# Multiple components can update everytime interval gets fired.
@app.callback(*callback_outputs, Input("interval-component", "n_intervals"))
def update_graphs(n):

    graph_df = pd.read_csv(config["file"], sep=";")

    data_time = list(graph_df["time"])

    figs = list()
    for name,y_column in y_columns.items():
        fig = plotly.tools.make_subplots(rows=1, cols=1, vertical_spacing=0.1)
        fig["layout"]["title"] = {
            "x": .1, "y": .9,
        }
        fig["layout"]["margin"] = {
            "l": 20, "r": 10, "b": 30, "t": 10
        }
        fig["layout"]["legend"] = {"x": 0, "y": 1, "xanchor": "left"}

        fig.append_trace({
            "x": data_time,
            "y": list(graph_df[y_column]),
            "name": name,
            "mode": "lines+markers",
            "type": "scatter"
        }, 1, 1)
        figs.append(fig)

    return figs

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)