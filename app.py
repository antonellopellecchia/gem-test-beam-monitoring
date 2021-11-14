import datetime
import yaml
import pandas as pd
import argparse

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly
import plotly.subplots

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


# split into more columns
if config["twocolumns"]:
    for y_column1,y_column2 in zip(y_columns[0::2], y_columns[1::2]):
        div_graphs.append(html.Div(
            className = "row",
            children = [
                html.Div(
                    children = [
                        dcc.Graph(
                            id=f"{y_column1['channel']}-graph",
                            style = {
                                "width": "50%",
                                "float": "left"
                            }),
                        dcc.Graph(
                            id=f"{y_column2['channel']}-graph",
                            style = {
                                "width": "50%",
                                "float": "left"
                            }),
                    ]
                )
            ]
        ))
        callback_outputs.append(Output(f"{y_column1['channel']}-graph", "figure"))
        callback_outputs.append(Output(f"{y_column2['channel']}-graph", "figure"))
else:
    for y_column in y_columns:
        div_graphs.append(html.Div(y_column["name"]))
        div_graphs.append(dcc.Graph(id=f"{y_column['channel']}-graph"))
        callback_outputs.append(Output(f"{y_column['channel']}-graph", "figure"))

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
    for y_column in y_columns:
        fig = plotly.subplots.make_subplots(rows=1, cols=1, vertical_spacing=0.1)
        fig["layout"]["title"] = {
            "x": .1, "y": .9,
        }
        fig["layout"]["margin"] = {
            "l": 20, "r": 10, "b": 30, "t": 10
        }
        fig["layout"]["legend"] = {"x": 0, "y": 1, "xanchor": "left"}

        fig.append_trace({
            "x": data_time,
            "y": list(graph_df[y_column["channel"]]),
            "name": y_column["name"],
            "mode": "lines+markers",
            "type": "scatter",
        }, 1, 1)
        fig.update_xaxes(title_text=x_column, row=1, col=1)
        fig.update_yaxes(title_text=y_column["name"], row=1, col=1)
        fig.update_traces(line={"color":y_column["color"]})
        figs.append(fig)

    return figs

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=8080)