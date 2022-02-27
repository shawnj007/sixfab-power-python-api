import os
import sys
sys.path.append('/home/pi/gits/sixfab-power-python-api/')

from power_api import SixfabPower, Definition, Event
api = SixfabPower()

print("Powering down")

status = 1
while True:
	try:
		api.set_edm_status(status, 1000)
	except:
		print("failed")
