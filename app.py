#!/bin/python3

import time
import yaml
import json
import argparse

from modules.lv_power_supply import GPIBPowerSupply

from bottle import route, run, template, view

lv_supplies = list()

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='configuration file path')
    args = parser.parse_args()

    with open(args.config, 'r') as config_stream:
        config = yaml.safe_load(config_stream)

    for lv_supply in config['modules']['lv_power_supplies']:
        lv_supplies.append(GPIBPowerSupply(lv_supply['name'], lv_supply['host']))
        lv_supplies[-1].connect()

    run(host='localhost', port=8080, debug=True)
    
    #while True:
        #for lv_supply in lv_supplies:
            #print(lv_supply.name, lv_supply.voltage, lv_supply.current)
        #time.sleep(1)
        #print('.....')

if __name__=='__main__': main()