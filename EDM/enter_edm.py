import sys
sys.path.append('/home/pi/gits/sixfab-power-python-api/')

from power_api import SixfabPower, Definition, Event

print("Powering down")
while True:
	try:
		api = SixfabPower()
		print("success" if api.set_edm_status(1, 500) == 1 else "failed")
	except:
		print("exception")
