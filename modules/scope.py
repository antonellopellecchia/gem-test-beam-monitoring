import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import vxi11

class Scope:

    def from_config(config):
        if config["class"] == "lecroy":
            return ScopeLecroy(config["hostname"])
        elif config["class"] == "rto":
            return ScopeRTO(config["hostname"])

    def save_event_raw(self, output_path, mode="w"):
        event_raw = self.get_event_raw()
        with open(output_path, mode) as output_file:
            output_file.write(event_raw)

class ScopeRTO(Scope):

    channels = 4

    def __init__(self, hostname):
        self.hostname = hostname
        self.scope = vxi11.Instrument(hostname)

    def get_event_raw(self):
        # get raw event from all channels
        event_raw = f"CHANNELS:{self.channels}/"#.encode()
        for channel in range(1, self.channels+1):
            channel_header = f"CH{channel:02}"#.encode()
            waveform_raw = self.get_waveform_raw(channel)
            event_raw += channel_header+"_"+waveform_raw+"/"
        return event_raw

    def get_waveform_raw(self, channel, wf_format="ascii"):
        # gets last triggered waveform from chosen channel
        if wf_format=="ascii": # sloooow
            self.scope.write(f'CHAN{channel}:DATA:HEAD?')
            waveform_header = self.scope.read()
            self.scope.write(f'CHAN{channel}:DATA?')
            waveform_content = self.scope.read()
            return f"{waveform_header}_{waveform_content}"
        elif wf_format=="raw":
            self.scope.write(f'CHAN{channel}:DATA:HEAD?')
            waveform_header = self.scope.read()
            self.scope.write(f'CHAN{channel}:DATA?')
            waveform_content = self.scope.read_raw()
            #print(waveform_content.decode())
            return waveform_header.encode()+b"_"+waveform_content
        else: raise ValueError(f"Unknown waveform wf_format: {wf_format}")

class ScopeLecroy(Scope):

    def __init__(self, hostname):
        self.hostname = hostname
        self.scope = vxi11.Instrument(hostname)

        print('Initializing communication to scope...')
        self.scope.write('TRMD?')
        print('Trigger', self.scope.read())

    def configure(self):
        # prepare scope for waveform acquisition and transfer
        self.scope.write("WFSU SP, 1, NP, 0, FP, 0, SN, 0")

    @property
    def trigger_mode(self):
        self.scope.write('TRMD?')
        return self.scope.read()

    @trigger_mode.setter
    def trigger_mode(self, mode):
        self.scope.write(f'TRMD {mode}')
        if not self.trigger_mode==mode:
            raise ConnectionError('Error setting trigger mode')
    
    @property
    def triggered(self):
        # tells whether the scope has triggered since the last poll
        self.scope.write('CHDR OFF')
        self.scope.write('INR?')
        has_triggered = self.scope.read()
        return has_triggered!='0'

    def set_threshold(self, channel, threshold, edge='NEG'):
        # set trigger slope, channel and threshold in mV
        self.scope.write(f'TRSL {edge}')
        self.scope.write(f'TRIG_SELECT EDGE,SR,{channel}')
        self.scope.write(f'{channel}:TRIG_LEVEL {threshold} mV')

    def get_waveform(self, channel):
        # gets last triggered waveform from chosen channel
        self.scope.write(f'{channel}:WF?')
        scope_response = self.scope.read_raw()
        return Waveform.unpack(scope_response, format='IEEE488.2')
    
class Event:

    def __init__(self, waveforms):
        self.waveforms = waveforms
    
    def from_raw(event_list, format):
        #print(event_list)
        if format=="rto":
            # parse event header:
            event_list.pop(0)

            waveforms = list()
            for event_string in event_list:
                wf = Waveform.unpack(event_string, format="rto")
                waveforms.append(wf)
            return Event(waveforms)

        else: raise TypeError("Unknown event format")

    def to_dataframe(self):
        wf_dict = {
            "time": self.waveforms[0].x
        }
        for channel,waveform in enumerate(self.waveforms):
            wf_dict[f"ch{channel}"] = waveform.y
        event_df = pd.DataFrame.from_dict(wf_dict)
        print(event_df)
        return event_df

class Waveform:

    def __init__(self, x, y):
        self.x, self.y = x, y

    def unpack(packet, format):
        if format=='IEEE488.2':
            """Unpack scope standard waveform"""

            # apply offset to response packet
            start = packet.find(b'WAVEDESC')
            packet = packet[start:]

            packet_length = np.frombuffer(packet[60:64], dtype=np.uint32)
            wf_length = int(packet_length/2)
            x = np.arange(wf_length, dtype=np.float64)
            y = np.frombuffer(packet[346:], dtype=np.int16, count=wf_length).astype(np.float64)

            x_gain = np.frombuffer(packet[176:180], dtype=np.float32)
            x_offset = np.frombuffer(packet[180:188], dtype=np.float64)
            x *= x_gain
            x += x_offset
            x *= 1e9

            y_gain = np.frombuffer(packet[156:160], dtype=np.float32)
            y_offset = np.frombuffer(packet[160:164], dtype=np.float32)
            y *= y_gain
            y -= y_offset

        elif format=="rto":
            [channel_header, waveform_header, payload] = packet.split("_")

            # parse wf heaader
            tstart, tstop, ntimes, _ = waveform_header.split(",")
            tstart, tstop, ntimes = float(tstart), float(tstop), int(ntimes)
            x = np.linspace(tstart, tstop, ntimes)

            # parse wf payload
            voltages = payload.split(",")
            y = np.array([ float(v) for v in voltages ])
            
        else: raise ValueError('Unrecognized waveform packet format')
        
        return Waveform(x, y)
    
    def __len__(self):
        return self.x.size

    def __add__(self, offset):
        result_wf = Waveform(self.x, self.y+offset)
        return result_wf

    def __sub__(self, offset):
        return self + (-offset)

    @property
    def min(self):
        return min(self.y)

    @property
    def max(self):
        return max(self.y)

    @property
    def baseline(self):
        baseline_stop = int(0.3*len(self))
        baseline_points = self.y[:baseline_stop]
        return baseline_points.mean()

    @property
    def charge(self):
        return sum(self.y)*(self.x[1]-self.x[0])/50

    def subtract_baseline(self):
        return self - self.baseline

    def save_figure(self, figure_path):
        fig = plt.figure()
        plt.plot(self.x, self.y)
        plt.xlabel('Time (ns)')
        plt.ylabel('Voltage (mV)')
        fig.savefig(figure_path)