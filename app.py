import datetime

import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4("CMS GEM test beam monitor"),
        html.Div(id="live-update-text"),
        dcc.Graph(id="rate-graph"),
        html.Div("VFAT error monitoring"),
        dcc.Graph(id="vfat-error-graph"),
        html.Div("Low voltage monitoring"),
        dcc.Graph(id="low-voltage-graph"),
        dcc.Interval(
            id="interval-component",
            interval=5*1000, # in milliseconds
            n_intervals=0
        )
    ])
)


"""@app.callback(Output("live-update-text", "children"),
              Input("interval-component", "n_intervals"))
def update_metrics(n):
    lon, lat, alt = satellite.get_lonlatalt(datetime.datetime.now())
    style = {"padding": "5px", "fontSize": "16px"}
    return [
        html.Span("Longitude: {0:.2f}".format(lon), style=style),
        html.Span("Latitude: {0:.2f}".format(lat), style=style),
        html.Span("Altitude: {0:0.2f}".format(alt), style=style)
    ]"""


# Multiple components can update everytime interval gets fired.
@app.callback(Output("low-voltage-graph", "figure"), Input("interval-component", "n_intervals"))
def update_lv_graph(n):

    # Collect some data

    # Create the graph with subplots
    fig = plotly.tools.make_subplots(rows=2, cols=2, vertical_spacing=0.1)
    fig["layout"]["title"] = {
        "x": .1, "y": .9,
    }
    fig["layout"]["margin"] = {
        "l": 20, "r": 10, "b": 30, "t": 10
    }
    fig["layout"]["legend"] = {"x": 0, "y": 1, "xanchor": "left"}

    log_df = pd.read_csv("log/testbeam.log", sep=";")
    for row,device in enumerate(["tracker", "chambers"]):
        log_device = log_df[log_df["name"]==device].tail(200)

        data_time = list(log_device["time"]-log_df.iloc[0]["time"])
        fig.append_trace({
            "x": data_time,
            "y": list(log_device["voltage"]),
            "name": f"{device} voltage",
            "mode": "lines+markers",
            "type": "scatter"
        }, row+1, 1)
        fig.append_trace({
            "x": data_time,
            "y": list(log_device["current"]),
            "name": f"{device} current",
            "mode": "lines+markers",
            "type": "scatter"
        }, row+1, 2)

    return fig

# Multiple components can update everytime interval gets fired.
@app.callback(Output("rate-graph", "figure"), Input("interval-component", "n_intervals"))
def update_rate_graph(n):

    # Collect some data
    log_df = pd.read_csv("log/xdaq.log", sep=";")
    log_device = log_df.tail(200)
    l1a_rate = int(log_df.iloc[-1]["L1A_RATE"])

    # Create the graph with subplots
    fig = plotly.tools.make_subplots(rows=1, cols=2, vertical_spacing=0.1)

    # L1A count
    fig["layout"]["title"] = {
        "x": .03, "y": .95,
        "text": f"L1A rate: {l1a_rate} Hz"
    }
    fig["layout"]["margin"] = {
        "l": 30, "r": 10, "b": 30, "t": 10
    }
    fig["layout"]["legend"] = {"x": .01, "y": .9, "xanchor": "left"}

    xdaq_time = list(log_device["time"]-log_device.iloc[0]["time"])
    fig.append_trace({
        "x": xdaq_time,
        "y": list(log_device["L1A_ID"]),
        "name": "L1A count",
        "mode": "lines+markers",
        "type": "scatter"
    }, 1, 1)

    # L1A rate
    l1a_rate_df = log_df[log_df["L1A_RATE"]!=0].tail(200)
    fig.append_trace({
        "x": list(l1a_rate_df["time"])-l1a_rate_df.iloc[0]["time"],
        "y": list(l1a_rate_df["L1A_RATE"]),
        "name": "L1A rate",
        "mode": "lines+markers",
        "type": "scatter"
    }, 1, 2)

    return fig

# Multiple components can update everytime interval gets fired.
@app.callback(Output("vfat-error-graph", "figure"), Input("interval-component", "n_intervals"))
def update_vfat_err(n):

    # Collect some data
    log_df = pd.read_csv("log/xdaq.log", sep=";")
    log_device = log_df.tail(50)

    # Create the graph with subplots
    fig = plotly.tools.make_subplots(rows=1, cols=2, vertical_spacing=0.1)

    # L1A count
    fig["layout"]["title"] = {
        "x": .03, "y": .95,
        #"text": "VFAT error counters"
    }
    fig["layout"]["margin"] = {
        "l": 30, "r": 10, "b": 30, "t": 10
    }
    fig["layout"]["legend"] = {"x": .01, "y": .9, "xanchor": "left"}

    xdaq_time = list(log_device["time"]-log_device.iloc[0]["time"])

    vfat_sync_err = list(
        sum([
            sum([log_device[f"OH{ohn}.VFAT{vfatn}.SYNC_ERR_CNT"] for vfatn in range(12)])
            for ohn in [0, 2, 3]
        ])
    )
    fig.append_trace({
        "x": xdaq_time,
        "y": vfat_sync_err,
        "name": "Sync errors",
        "mode": "lines+markers",
        "type": "scatter"
    }, 1, 1)
    vfat_crc_err = list(
        sum([
            sum([log_device[f"OH{ohn}.VFAT{vfatn}.DAQ_CRC_ERROR_CNT"] for vfatn in range(12)])
            for ohn in [0, 2, 3]
        ])
    )
    fig.append_trace({
        "x": xdaq_time,
        "y": vfat_crc_err,
        "name": "CRC errors",
        "mode": "lines+markers",
        "type": "scatter"
    }, 1, 2)

    return fig

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)