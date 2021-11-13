#!/bin/python3

import os, sys
import time
import argparse
import yaml

from modules import scope

import numpy as np
import pandas as pd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="raw file source")
    parser.add_argument("--config", help='configuration file path')
    parser.add_argument("--online", action="store_true", help="continuously unpack last event")
    parser.add_argument("output", help="output waveform file")
    args = parser.parse_args()

    with open(args.config, "r") as config_stream:
        config = yaml.safe_load(config_stream)
    outdir = config["output_dir"]

    if args.online:
        print("Running in DQM mode")

    try:
        while True:
            if args.online:
                # ignore input argument and use last file
                current_run_file = f"{outdir}/current_run.txt"
                try:
                    with open(current_run_file, "r") as current_run_stream:          
                        run_directory = current_run_stream.read()
                    event_files = sorted(os.listdir(run_directory))
                    args.input = f"{run_directory}/{event_files[-1]}"
                    args.output = config["monitoring"]["file"]
                except (IndexError,FileNotFoundError):
                    print("Run has disappeared, waiting...")
                    time.sleep(1)
                    continue

            print(f"Reading {args.input} and writing to {args.output}\t\t", end="\r")

            with open(args.input, "r") as input_stream:
                event_list = input_stream.read().split("/")
                event_list.remove("")
                if len(event_list) == 0: continue
                event = scope.Event.from_raw(event_list, format="rto")
                event.to_dataframe().to_csv(args.output, sep=";")
            if args.online: time.sleep(1)
            else: break
    except KeyboardInterrupt: print("")

if __name__=='__main__': main()