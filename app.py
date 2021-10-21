#!/bin/python3

import yaml
import argparse
from modules.lv_power_supply import GPIBPowerSupply

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='configuration file path')
    args = parser.parse_args()

    config = yaml.load(args.config)
    print(config)
    #lv_supply = GPIBPowerSupply

if __name__=='__main__': main()