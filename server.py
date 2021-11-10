#!/bin/python3

import time
import yaml
import json
import argparse

from modules.lv_power_supply import GPIBPowerSupply

import base64
from io import BytesIO
from flask import Flask, Response, render_template

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import pandas as pd

app = Flask(__name__)

lv_supplies = list()
lv_data = dict()

@app.route('/')
def index():
    devices = app.setup_config["modules"]["lv_power_supplies"]
    return render_template("index.html", devices=devices)

@app.route('/lv/')
def lv_monitoring():
    lv_values = list()
    for lv_supply in lv_supplies:
        lv_values.append({
            'name': lv_supply.name,
            'voltage': lv_supply.voltage,
            'current': lv_supply.current
        })
    return {'data': lv_values}

@app.route("/lv/plot/<name>/<variable>.png")
def lv_plot(name, variable):

    # retrieve monitoring data:
    log_df = pd.read_csv("log/testbeam.log", sep=";")
    log_device = log_df[log_df["name"]==name]

    """data = lv_monitoring()['data']
    current_time = time.time()
    for lv_supply in data:
        supply_name = lv_supply['name']
        if supply_name != name: continue
        if not name in lv_data:
            lv_data[name] = dict()
            lv_data[name]['time'] = list()
            lv_data[name]['voltage'] = list()
            lv_data[name]['current'] = list()
        lv_data[name]['time'].append(current_time)
        lv_data[name]['voltage'].append(lv_supply['voltage'])
        lv_data[name]['current'].append(lv_supply['current'])
        break"""
    
    # plot data for lv supply
    fig = Figure()
    ax = fig.subplots()
    log_time = log_device["time"] - int(log_device.iloc[0]["time"])
    ax.plot(log_time, log_device[variable])
    ax.set_xlabel("Time (s)")
    if variable == "voltage":
        ax.set_ylim(0, 10)
        ax.set_ylabel("Voltage (V)")
    elif variable == "current":
        ax.set_ylim(0, 5)
        ax.set_ylabel("Current (A)")
    output = BytesIO()
    #fig.savefig(output, format="png")
    #data = base64.b64encode(buf.getbuffer()).decode("ascii")
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")
    #return f"<img src='data:image/png;base64,{data}'/>"
    #return send_file(buf, mimetype="image/png")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='configuration file path')
    args = parser.parse_args()

    with open(args.config, 'r') as config_stream:
        app.setup_config = yaml.safe_load(config_stream)

    """for lv_supply in config['modules']['lv_power_supplies']:
        lv_supplies.append(GPIBPowerSupply(lv_supply['name'], lv_supply['host']))
        lv_supplies[-1].connect()"""

    app.run(host='0.0.0.0', port=8080, debug=True)
    
    #while True:
        #for lv_supply in lv_supplies:
            #print(lv_supply.name, lv_supply.voltage, lv_supply.current)
        #time.sleep(1)
        #print('.....')

if __name__=='__main__':
    main()