#!/bin/python3

import os, sys
import time
import yaml
import json
import argparse
import socket
import requests

import curses
import prompt_toolkit

import numpy as np

from modules import hv
from modules import scope
import labsetup

ftm_setup = labsetup.LabSetup()

def daq_execute(command):
    command_list = command.split(" ")
    if command_list[0] == "exit": sys.exit(0)
    elif command_list[0] == "hv":
        if command_list[1] == "status": print(ftm_setup.status_table())
        elif command_list[1] == "set":
            board, channel, param, value = command_list[2:6]
            print(ftm_setup.hv.boards[int(board)].set_parameter(channel, param, value), end="")
        elif command_list[1] == "get":
            board, channel, param = command_list[2:5]
            print(ftm_setup.hv.boards[int(board)].get_parameter(channel, param), end="")
        elif command_list[1] == "on":
            board, channel = command_list[2:4]
            print(ftm_setup.hv.boards[int(board)].turn_on(channel), end="")
        elif command_list[1] == "off":
            board, channel = command_list[2:4]
            print(ftm_setup.hv.boards[int(board)].turn_off(channel), end="")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='configuration file path')
    args = parser.parse_args()

    with open(args.config, 'r') as config_stream:
        config = yaml.safe_load(config_stream)
    
    outdir = config["output_dir"]
    os.makedirs(outdir, exist_ok=True)

    for hv_dict in config["modules"]["hv"]:
        name, port, board = hv_dict["name"], hv_dict["port"], hv_dict["board"]
        ftm_setup.hv.add(hv.BoardCaen(name, port, board))
    #ftm_setup.scope = scope.Scope.from_config(config["modules"]["scope"])

    # screen.clear()
    # screen.addstr(ftm_setup.status_table().__str__())
    # screen.refresh()

    prompt_session = prompt_toolkit.PromptSession()
    previous_command = ""
    try:
        while True:
            try:
                command = prompt_session.prompt('[daq]$ ')
                if command == "": command = previous_command
                previous_command = command
                daq_execute(command)
            except KeyboardInterrupt: pass
    except EOFError: pass

if __name__=='__main__': main()