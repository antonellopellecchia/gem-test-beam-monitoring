#!/bin/python3

import os
import time
import yaml
import json
import argparse
import socket

import requests

import numpy as np

from modules.lv_power_supply import GPIBPowerSupply

lv_supplies = list()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='configuration file path')
    args = parser.parse_args()

    with open(args.config, 'r') as config_stream:
        config = yaml.safe_load(config_stream)

    for lv_supply in config['modules']['lv_power_supplies']:
        lv_supplies.append(GPIBPowerSupply(lv_supply['name'], lv_supply['host']))
        try:
            lv_supplies[-1].connect()
        except socket.timeout:
            print(f"Error connecting to {lv_supply['name']}, retrying in 2 s...")
            time.sleep(2)
            lv_supplies[-1].connect()            
    
    log_file_path = config["log_file"]
    xdaq_file_path = config["xdaq_file"]
    xdaq_url = "http://"+config["xdaq_url"]+"/"+config["xdaq_monitor_page"]

    if not os.path.exists(xdaq_file_path):
        print(f"Creating output file {xdaq_file_path}...")
        xdaq_request = requests.get(xdaq_url)
        xdaq_json = xdaq_request.json()
        with open(xdaq_file_path, "w") as xdaqfile:
            xdaqfile.write("time;")
            for key in xdaq_json: xdaqfile.write(key+";")
            xdaqfile.write("\n")
    else:
        print(f"Appending to {xdaq_file_path}...")

    if not os.path.exists(log_file_path):
        print(f"Creating output file {log_file_path}...")
        with open(log_file_path, "w") as logfile:
            logfile.write("time;name;voltage;current\n")
    else:
        print(f"Appending to {log_file_path}...")

    print("..................")
    sleep_time = config["sleep_time"]
    while True:
        current_time = int(time.time())
        
        # log LV monitoring
        with open(log_file_path, "a") as logfile:
            try:
                for lv_supply in lv_supplies:
                    name, voltage, current = lv_supply.name, lv_supply.voltage, lv_supply.current
                    if "A" in voltage or "V" in current:
                        print(f"Data corrupted for {name}, discarding...")
                        continue
                    print(name, voltage, current)
                    logfile.write(";".join(
                        np.array([
                            current_time,
                            name,
                            voltage.replace("V", ""),
                            current.replace("A", "")
                        ]).astype(str)
                    ))
                    logfile.write("\n")
            except BrokenPipeError:
                print("Error querying device, skipping point...")
            except socket.timeout:
                print("Error querying device, skipping point...")
        
        # log DQM monitoring
        try:
            xdaq_request = requests.get(xdaq_url)
            xdaq_json = xdaq_request.json()
            with open(xdaq_file_path, "a") as xdaqfile:
                xdaqfile.write(f"{current_time};")
                print("L1A_RATE", xdaq_json["L1A_RATE"])
                for key,element in xdaq_json.items(): xdaqfile.write(f"{element};")
                xdaqfile.write("\n")
        except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError, TypeError, KeyError) as e:
            print("Error querying xdaq, skipping point:", e)
        print("..................")
        time.sleep(sleep_time)

if __name__=='__main__': main()