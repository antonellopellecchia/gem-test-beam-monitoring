from plx_gpib_ethernet import PrologixGPIBEthernet

class GPIBPowerSupply:
    PORT = 1234

    def __init__(self, ip):
        self.ip = ip
        self.device = PrologixGPIBEthernet(tracking)
    
    def connect(self):
        self.gpib.connect()
        self.gpib.select(6)

    def get_voltage(self):
        voltage = self.device.query("VO?")
        return voltage.strip()

    def get_current(self):
        current = self.device.query("IO?")
        return current.strip()