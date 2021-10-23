#!/bin/python3

import time
import yaml
import json
import argparse

from modules.lv_power_supply import GPIBPowerSupply

import base64
from io import BytesIO
from bottle import route, run, template, view
from matplotlib.figure import Figure

lv_supplies = list()

lv_data = dict()

@route('/')
@view('index')
def index():
    return dict()

@route('/lv/')
def lv_monitoring():
    lv_values = list()
    for lv_supply in lv_supplies:
        lv_values.append({
            'name': lv_supply.name,
            'voltage': lv_supply.voltage,
            'current': lv_supply.current
        })
    return {'data': lv_values}

@route("/lv/plot/<name>/<variable>")
def lv_plot(name, variable):
    current_time = time.time()

    # retrieve monitoring data:
    data = lv_monitoring()['data']
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
        break
    
    # plot data for lv supply
    fig = Figure()
    ax = fig.subplots()
    ax.plot(lv_data[name]['time'], lv_data[name]['voltage'])
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='configuration file path')
    args = parser.parse_args()

    with open(args.config, 'r') as config_stream:
        config = yaml.safe_load(config_stream)

    for lv_supply in config['modules']['lv_power_supplies']:
        lv_supplies.append(GPIBPowerSupply(lv_supply['name'], lv_supply['host']))
        lv_supplies[-1].connect()

    run(host='0.0.0.0', port=8080, debug=True, reloader=True)
    
    #while True:
        #for lv_supply in lv_supplies:
            #print(lv_supply.name, lv_supply.voltage, lv_supply.current)
        #time.sleep(1)
        #print('.....')

if __name__=='__main__': main()