import os
import sys
import time
import datetime
import subprocess
sys.path.append('./')
#from power_api import SixfabPower, Definition, Event

sys.path.append('../gpsd-py3')
import gpsd

sys.path.append('../openauto-pro-api/api_examples/python')
import common.Api_pb2 as oap_api

#api = SixfabPower()

ENABLE_SHUTDOWN = False

ENABLE_SHUTDOWN_EVENT = False
ENABLE_SHUTDOWN_COMMAND = True

BLANK_LCD = False

FORCE_GPS_SET = False
FORCE_RTC_SET = False
FORCE_SYS_SET = False

dt_sys = datetime.datetime.fromtimestamp(int(time.time()))

GET_OAP = False
if GET_OAP:
	set_day_night = oap_api.SetDayNight()
	night = set_day_night.android_auto_night_mode
else:
	night = False

GET_UPS = False
if GET_UPS:
	temps = (api.get_input_temp(),    api.get_system_temp(),    api.get_battery_temp())
	volts = (api.get_input_voltage(), api.get_system_voltage(), api.get_battery_voltage())
	currs = (api.get_input_current(), api.get_system_current(), api.get_battery_current())
	powrs = (api.get_input_power(),   api.get_system_power(),   api.get_battery_power())
	lvls  = (api.get_battery_level(), api.get_battery_max_charge_level())
	
	dt_rtc = int(api.get_rtc_time(Definition.TIME_FORMAT_EPOCH))
else:
	temps = (0.0, 0.0, 0.0)
	volts = (0.0, 0.0, 0.0)
	currs = (0.0, 0.0, 0.0)
	powrs = (0.0, 0.0, 0.0)
	lvls = (0.0, 0.0)
	
	dt_rtc = int(0)

GET_GPS = False
if GET_GPS:
	gpsd.connect()
	packet = gpsd.get_current()
	
	gps_modes = dict()
	gps_modes[0] = "No Sat"
	gps_modes[1] = "No Fix"
	gps_modes[2] = "2D Fix"
	gps_modes[3] = "3D Fix"
	gps_mode = gps_modes[packet.mode]
	
	sat = packet.sats
	
	if packet.mode >= 2:
		gps_lat = packet.lat
		gps_lon = packet.lon
		gps_tim = packet.time_local() 	# datetime
		gps_spd = packet.hspeed
		gps_trk = packet.track
		gps_eps = packet.error['eps']
		gps_ept = packet.error['ept']
		gps_epx = packet.error['epx']
		gps_epy = packet.error['epy']
	else:
		gps_lat = float("nan")
		gps_lon = float("nan")
		gps_tim = float("nan")
		gps_spd = float("nan")
		gps_trk = float("nan")
		gps_eps = float("nan")
		gps_ept = float("nan")
		gps_epx = float("nan")
		gps_epy = float("nan")
	
	if packet.mode >= 3:
		gps_alt = packet.alt
		gps_clm = packet.climb
		gps_ecp = packet.error['ecp']
		gps_epv = packet.error['epv']
	else:
		gps_alt = float("nan")
		gps_clm = float("nan")
		gps_ecp = float("nan")
		gps_epv = float("nan")

	mode0 = (str("%6d" % sats), gps_mode, "healthy" if api.get_fan_health() == 1 else "broken", api.get_battery_health())
	mode1 = (gps_spd, api.get_fan_speed(), api.get_battery_design_capacity())
	mode2 = (gps_lat, gps_epy, api.get_fan_mode())
	mode3 = (gps_lon, gps_epx, api.get_fan_automation()[0], api.get_fan_automation()[1])
	mode4 = (gps_alt, gps_epv)
	
	dt_gps = datetime.datetime.fromtimestamp(int(gps_tim))
	
else:
	mode0 = ("No GPS", 0, 0, 0)
	mode1 = (float("nan"), 0, 0, 0)
	mode2 = (float("nan"), 0, 0)
	mode3 = (float("nan"), 0, 0, 0)
	mode4 = (float("nan"), 0)
	
	gps_tim = 0
	gps_spd = 0
	gps_trk = 0
	gps_clm = 0
	gps_ept = float("nan")
	dt_gps = datetime.datetime.fromtimestamp(int(gps_tim))

if GET_UPS:
	rtc_date = api.get_rtc_time(Definition.TIME_FORMAT_DATE)
	rtc_time = api.get_rtc_time(Definition.TIME_FORMAT_TIME)
else:
	rtc_date = "??"
	rtc_time = "??"

print("|***** Input Sensors *****|**** System Sensors *****|**** Battery Sensors ****|")
print("|     Temp: %5.2f °C      |       Temp: %5.2f °C    |       Temp: %5.2f °C    |" % temps)
print("|  Voltage: %5.2f V       |    Voltage: %5.2f V     |    Voltage: %5.2f V     |" % volts)
print("|  Current: %5.2f A       |    Current: %5.2f A     |    Current: %5.2f A     |" % currs)
print("|    Power: %5.2f W       |      Power: %5.2f W     |      Power: %5.2f W     |" % powrs)
print("|********** GPS **********|********** Fan **********|  Level/Max:   %3d %%/%3d |" % lvls)
print("|  Mode: %s  Vis: %3s |     Health:  %7s    |     Health:   %3d %%     |" % mode0)
print("| Lat:%8.3f° epy:%3dm  |      Speed: %5d RPM   |   Capacity:  %4d mAh   |" % mode1)
print("| Lon:%8.3f° eox:%3dm  |       Mode: %5d       |                         |" % mode2)
print("| Alt: %7.1fm epv:%3dm  | Thresholds:[%3d,%3d] °C |                         |" % mode3)
print("| Spd: %5.1fm/s eps: %2dm/s|***** Sys Date Time *****|***** RTC Date Time *****|" % mode4)

epoch = (int(gps_tim), gps_ept, int(time.time()), dt_rtc)
print("| dt:%10s ept: %4sS|     Epoch :  %10s |     Epoch :  %10s |" % epoch)

line = (gps_trk, dt_sys.strftime("%Y-%m-%d"), rtc_date)
print("| Track: %6.0f°          |   -> date :  %10s |   -> date :  %10s |" % line)

line = (gps_clm, dt_sys.strftime("%H:%M:%S"), rtc_time)
print("| Climb: %3.0fm/s ecp:      |   -> time :    %8s |   -> time :    %8s |" % line)

line = ( dt_sys, datetime.datetime.fromtimestamp(dt_rtc))
print("|                         |  lc %19s |  lc %19s |"% line)

print("|*************************|*************************|*************************|")

t = dt_sys

SET_TIME = False
if SET_TIME:
	if t - 2 < dt_gps or FORCE_GPS_SET:
		print("set using GPS time")
		t = int(gps_tim)
		FORCE_RTC_SET = True
		FORCE_SYS_SET = True

	if t - 2 > dt_rtc or FORCE_RTC_SET:
		print("sys -> RTC")
		api.set_rtc_time(t)
		print("api.set_rtc_time(int(time.time()+time.timezone))")

	if dt_rtc - 2 > t or FORCE_SYS_SET:
		print("RTC -> sys")
		cmd = str("sudo timedatectl set-ntp no")
		print(cmd)
		os.system(cmd)
		dt = datetime.datetime.fromtimestamp(api.get_rtc_time(Definition.TIME_FORMAT_EPOCH))
		cmd = str("sudo timedatectl set-time '"+str("%s" % (dt))+"'")
		print(cmd)
		os.system(cmd)
		cmd = str("sudo timedatectl set-ntp yes")
		print(cmd)
		os.system(cmd)

SEND_TEMP = False
if SEND_TEMP:		
	api.send_system_temp()

if ENABLE_SHUTDOWN and api.get_working_mode() == Definition.BATTERY_POWERED and api.get_input_power() <= 0.:
	print("Result removing all Scheduled Event: " + str(api.remove_all_scheduled_events(200)))
		
	print("Powering down")
	
	"""
	level, status = 50, 2
	api.set_safe_shutdown_battery_level(level)
	api.set_safe_shutdown_status(status)
	"""

	sleep_time, run_time = 1439, 0
	api.set_power_outage_params(sleep_time, run_time)
	
	#status = 2
	#api.set_lpm_status(status)

	# create power off event
	
	if ENABLE_SHUTDOWN_EVENT:
		print("Creating event")
		event = Event()
		event.id = 1
		event.schedule_type = Definition.EVENT_INTERVAL
		event.repeat = Definition.EVENT_ONE_SHOT
		event.time_interval = 5
		event.interval_type = Definition.INTERVAL_TYPE_SEC
		event.action = Definition.HARD_POWER_OFF

		result = api.create_scheduled_event_with_event(event, 200)
	else:
		print("Shutdown event disabled")

	if ENABLE_SHUTDOWN_COMMAND:
		if subprocess.run(["systemctl", "is-active --quiet shutdown_edm.service || systemctl start shutdown_edm.service"]) == 0:
			print("EDM service active")
		print("Sending shutdown command")
		os.system("sleep 1 && sudo shutdown -h now &")
	else:
		print("Shutdown command disabled")

	if BLANK_LCD:
		os.system("vcgencmd set_backlight 0 0")
		os.system("vcgencmd display_power 0 0")
	else:
		print("Keeping LCD on for now")
	"""
	status = 1
	api.set_edm_status(status)
	"""
	print("Good byte")
	exit()
