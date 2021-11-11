import serial

class Instrument:

    def __init__(self,
        port,
        baud=9600,
        parity=serial.PARITY_NONE,
        xonxoff=True,
        endl='\r\n',
        timeout=None
    ):
        self.ser = serial.Serial(port, baud, parity=parity)
        self.ser.xonxoff = xonxoff
        if timeout: self.ser.timeout = timeout
        self.endl = endl
    
    def write(self, command):
        self.ser.write(command.encode())

    def read(self):
        result = self.ser.read_until(self.endl)
        #result = self.ser.read()
        return result.decode()
    
    def readline(self):
        result = self.ser.readline()
        return result.decode()

    def get_settings(self):
        return self.ser.get_settings()