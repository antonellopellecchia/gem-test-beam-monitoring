#!/bin/python3

import os
import time
import yaml
import argparse

from modules import hv
from modules import scope
import labsetup

lv_supplies = list()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='configuration file path')
    parser.add_argument('run', help='run name')
    args = parser.parse_args()

    with open(args.config, 'r') as config_stream:
        config = yaml.safe_load(config_stream)
    outdir = config["output_dir"]
    os.makedirs(f"{outdir}/{args.run}", exist_ok=True)

    ftm_setup = labsetup.LabSetup()
    for hv_dict in config["modules"]["hv"]:
        name, port, board = hv_dict["name"], hv_dict["port"], hv_dict["board"]
        ftm_setup.hv.add(hv.BoardCaen(name, port, board))
    ftm_setup.scope = scope.Scope.from_config(config["modules"]["scope"])

    current_run_file = f"{outdir}/current_run.txt"
    with open(current_run_file, "w") as current_run_stream:
        current_run_stream.write(f"{outdir}/{args.run}")

    event_count = 0
    try:
        while True:
            time.sleep(1)
            ftm_setup.scope.save_event_raw(f"{outdir}/{args.run}/{event_count:010}")
            event_count += 1
            print(f"Saving event {event_count}...", end="\r")
    except KeyboardInterrupt: pass
    finally: print(f"Saved {event_count} events.")

if __name__=='__main__': main()