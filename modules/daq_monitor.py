import requests as req
import json

pcucla = req.get("http://pcuclacvp13:20500/urn:xdaq-application:lid=6147800/jsonUpdate")

monitor = json.loads(pcucla.text)


def get_monitor(name):
	'''given name, returns value from daq monitor page'''
	return monitor[name]


test = get_monitor("L1A_ID")
print(test)







