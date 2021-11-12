#!/bin/python3

import os, sys
import time
import argparse

from modules import scope

import numpy as np
import pandas as pd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="raw file source")
    parser.add_argument("output", help="output waveform file")
    parser.add_argument("--online", action="store_true", help="continuously unpack last event")
    args = parser.parse_args()

    while True:
        with open(args.input, 'r') as input_stream:
            event_list = input_stream.read().split("/")
            event_list.remove("")
            if len(event_list) == 0: continue
            event = scope.Event.from_raw(event_list, format="rto")
            event.to_dataframe().to_csv(args.output, sep=";")
        if args.online: time.sleep(1)
        else: break

if __name__=='__main__':
    main()