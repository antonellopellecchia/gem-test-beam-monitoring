from protocols.serial import Instrument as SerialInstrument

from beautifultable import BeautifulTable

class HVBoards:

    def __init__(self, boards=list()):
        self.boards = boards
    
    def add(self, board):
        self.boards.append(board)
    
    # def repr_status(self):
    #     parameters = ["board", "channel", "vset", "vmon", "iset", "imon", "status"]
    #     status_str = ("{:<15} "*len(parameters)).format(*parameters)+"\n"
    #     for board in self.boards:
    #         for channel_status in board.get_status():
    #             status_str += ("{:<15} "*len(parameters)).format(*channel_status.values())+"\n"
    #     return status_str

    def status_table(self):
        parameters = ["board", "channel", "vset", "vmon", "iset", "imon", "status"]
        table = BeautifulTable()
        table.columns.header = parameters
        for board in self.boards:
            for channel_status in board.get_status():
                table.rows.append(channel_status.values())
        return table

class HVBoard: pass

class BoardCaen(HVBoard):
    
    parameters = ["VSET","VMON","ISET","IMON","STAT"]

    def __init__(self, name, port, board):
        self.name = name
        self.instrument = SerialInstrument(
            port=port,
            xonxoff = True,
            endl = '\r\n',
            #timeout = 0.1
        )
        self.board = board

    def get_settings(self):
        return self.instrument.get_settings()

    def send_command(self, command):
        self.instrument.write(command)
        response = self.instrument.readline()
        return response
    
    def parse_line(self, line):
        response_list = line.replace('\r\n', ',').split(',')
        try: response_list.remove('')
        except ValueError: pass

        response_pairs = [s.split(':') for s in response_list]
        response_dict = dict(response_pairs)
        return response_dict
        
    def parse_response(self, response, channels, parameters):
        response_lines = response.split("\r\n")
        response_lines.remove("")
        print(response_lines)
        responses = list()
        for channel in channels:
            responses.append({
                "board": self.name,
                "channel": channel
            })
            for parameter in parameters:
                response_line = response_lines.pop(0)
                print(channel, parameter, response_line)
                d = self.parse_line(response_line)
                responses[-1][parameter] = d["VAL"]

    def read_parameter(self, channel, parameter):
        command = f'$BD:{self.board},CMD:MON,CH:{channel},PAR:{parameter}\r\n'
        response = self.send_command(command)
        response_data = self.parse_line(response)
        return response_data['VAL']
    
    def set_parameter(self, channel, name, value):
        command = f'$BD:{self.board},CMD:SET,CH:{channel},PAR:{name},VAL:{value}\r\n'
        return self.send_command(command)

    def get_parameter(self, channel, name):
        command = f'$BD:{self.board},CMD:MON,CH:{channel},PAR:{name}\r\n'
        return self.send_command(command)
    
    def turn_on(self, channel):
        return self.send_command(f"$BD:{self.board},CMD:SET,CH:{channel},PAR:ON\r\n")

    def turn_off(self, channel):
        return self.send_command(f"$BD:{self.board},CMD:SET,CH:{channel},PAR:OFF\r\n")

    def set_voltage(self, channel, voltage):
        command = f'$BD:{self.board},CMD:SET,CH:{channel},PAR:VSET,VAL:{voltage}\r\n'
        self.instrument.write(command)
    
    def get_vset(self, channel):
        return float(self.read_parameter(channel, 'VSET'))
    
    def get_vmon(self, channel):
        return float(self.read_parameter(channel, 'VMON'))

    def get_iset(self, channel):
        return float(self.read_parameter(channel, 'ISET'))
    
    def get_imon(self, channel):
        return float(self.read_parameter(channel, 'IMON'))

    def get_status(self):
        channels = 4
        status = [
            {
                "board": self.name,
                "channel": channel
            }
            for channel in range(channels)
        ]
        #return [ self.get_status_channel(channel) for channel in range(channels) ]

        for parameter in BoardCaen.parameters:
            command = f'$BD:{self.board:02},CMD:MON,CH:{channels:02},PAR:{parameter}\r\n'
            parameter_response = self.parse_line(self.send_command(command))
            parameter_values = parameter_response["VAL"].split(";")
            parameter_values = [ float(v) for v in parameter_values ]
            for channel in range(channels):
                status[channel][parameter] = parameter_values[channel]
        return status

        print(self.instrument.ser)
        for parameter in parameters:
            l = self.instrument.ser.read(1000)
            print(l)
        return []
        response_raw = self.send_command(command)
        print(response_raw.encode())
        return []
        response = self.parse_response(response_raw, channels, parameters)
        

    def get_status_channel(self, channel):
        status_dict_channel = {
            "board": self.name,
            "channel": channel,
            "vset": self.get_vset(channel),
            "vmon": self.get_vmon(channel),
            "iset": self.get_iset(channel),
            "imon": self.get_imon(channel)
        }
        return status_dict_channel
