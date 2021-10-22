from plx_gpib_ethernet import PrologixGPIBEthernet

class GPIBPowerSupply:
    PORT = 1234

    def __init__(self, name, host):
        self.name = name
        self.host = host
        self.device = PrologixGPIBEthernet(self.host)
    
    def connect(self):
        self.device.connect()
        self.device.select(6)

    @property
    def voltage(self):
        voltage = self.device.query("VO?")
        return voltage.strip()

    @property
    def current(self):
        current = self.device.query("IO?")
        return current.strip()