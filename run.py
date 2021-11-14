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
    # for hv_dict in config["modules"]["hv"]:
    #     name, port, board = hv_dict["name"], hv_dict["port"], hv_dict["board"]
    #     ftm_setup.hv.add(hv.BoardCaen(name, port, board))

    ftm_setup.scope = scope.Scope.from_config(config["modules"]["scope"])
    
    # debugging stuff:
    #ftm_setup.scope.scope.write('TRIG:SOURCE CHAN3')
    #ftm_setup.scope.scope.write('TRIG:QUAL1:B 1')
    #    ftm_setup.scope.scope.write('TRIG1:QUAL1:STAT 1')
    #ftm_setup.scope.scope.write('TRIG2:QUAL1:STAT 1')
    # ftm_setup.scope.scope.write('TRIG:LEV 10e-3')
    # ftm_setup.scope.scope.write('TIM:SCAL 100e-9')
    # ftm_setup.scope.scope.write('TIM:POS 0')
    # ftm_setup.scope.scope.write('TIM:REF 0')
    # ftm_setup.scope.scope.write('TRIG:OFFS:LIM 0')
    #ftm_setup.scope.scope.write('TRIG:SEQ:MODE ABR')
    #ftm_setup.scope.scope.write('ACQ:POIN 3000')
    #ftm_setup.scope.scope.write('FORM ASC')
    #ftm_setup.scope.scope.write('RUN')

    print('Initializing communication to scope...')
    print(ftm_setup.scope.scope.ask('*IDN?'))
    ftm_setup.scope.scope.write('FORM?')
    print('Data format', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TRIG:MODE?')
    print('Trigger mode', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TRIG:SOURCE?')
    print('Trigger source', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TIM:SCAL?')
    print('Time scale', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TIM:POS?')
    print('Time pos', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TIM:REF?')
    print('Time ref', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('ACQ:RES?')
    print('Acquisition resolution', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('ACQ:POIN?')
    print('Acquisition points', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('ACQ:MODE?')
    print('Acquisition mode', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TRIG:TYPE?')
    print('Trigger type', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TRIG:OFFS:LIM?')
    print('Trigger offset limit', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TRIG:LEV?')
    print('Trigger level', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TRIG:EDGE:SLOPE?')
    print('Trigger edge slope', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TRIG:ROB?')
    print('Trigger robust', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TRIG2:QUAL1:STAT?')
    print('Trigger qual stat', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TRIG:QUAL:A?')
    print('Trigger qual A', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TRIG:QUAL:B?')
    print('Trigger qual B', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TRIG:QUAL:C?')
    print('Trigger qual C', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TRIG:QUAL:D?')
    print('Trigger qual D', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TRIG:QUAL:AB:LOG?')
    print('Trigger qual AB', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('TRIG:SEQ:MODE?')
    print('Trigger sequence mode', ftm_setup.scope.scope.read())
    ftm_setup.scope.scope.write('STAT:OPER?')
    print('Trigger status operation', format( int(ftm_setup.scope.scope.read()), "016b") )
    ftm_setup.scope.scope.write('*ESE?')
    print('Event status enable:', format( int(ftm_setup.scope.scope.read()), "016b") )
    ftm_setup.scope.scope.write('*ESR?')
    print('Event status register:', format( int(ftm_setup.scope.scope.read()), "016b") )
    ftm_setup.scope.scope.write('*SRE?')
    print('Status byte:', format( int(ftm_setup.scope.scope.read()), "016b") )

    current_run_file = f"{outdir}/current_run.txt"
    with open(current_run_file, "w") as current_run_stream:
        current_run_stream.write(f"{outdir}/{args.run}")

    event_count = 0
    # wait for new trigger
    #ftm_setup.scope.scope.write("*OPC")
    try:
        while True:
            #time.sleep(.1)

            stat_oper = int(ftm_setup.scope.scope.ask('STAT:OPER?'))
            trigger_mask = 0b0000000001000000
            has_triggered = (stat_oper & trigger_mask) >> 6
            #print('Trigger status operation', format(stat_oper, "016b"), format(has_triggered, "016b") )

            # have you triggered?
            # ftm_setup.scope.scope.write("*OPC?")
            # status_opc = ftm_setup.scope.scope.read()
            # print('Trigger status operation', status_opc)

            # ftm_setup.scope.scope.write("*STB?")
            # status_byte = int(ftm_setup.scope.scope.read())
            # print('Status byte', format(status_byte, "016b"))

            #ftm_setup.scope.scope.write("*ESR?")
            #esr = ftm_setup.scope.scope.read()
            # if esr != "0": 
            #   print("ESR", format(int(esr), "016b"))

            # ftm_setup.scope.scope.write("*OPC")
            if has_triggered:
                print(f"Saving event {event_count}...", end="\r")
                ftm_setup.scope.save_event_raw(f"{outdir}/{args.run}/{event_count:010}")
                event_count += 1
    except KeyboardInterrupt: pass
    finally: print(f"Saved {event_count} events.")

if __name__=='__main__': main()