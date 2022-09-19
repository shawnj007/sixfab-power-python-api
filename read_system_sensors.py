import os
import sys
import time
import math
import datetime
import subprocess
from termcolor import colored

sys.path.append('./')
from power_api.power_api import SixfabPower, Definition, Event

sys.path.append('../gpsd-py3')
import gpsd

sys.path.append('../openauto-pro-api/api_examples/python')
import common.Api_pb2 as oap_api

api = SixfabPower()

ENABLE_SHUTDOWN = True
REQUIRE_EDM_FOR_SHUTDOWN = True

ENABLE_SHUTDOWN_EVENT = False
ENABLE_SHUTDOWN_COMMAND = True

BLANK_LCD = True

FORCE_GPS_SET = False
FORCE_RTC_SET = False
FORCE_SYS_SET = False

SEND_CONFIG = False
if SEND_CONFIG:
	api.set_battery_max_charge_level(95)
	api.set_battery_design_capacity(3000)
	api.set_fan_automation(45,55)
	api.set_fan_mode(3)
	#sleep_time, run_time = 1439, 0
	#api.set_power_outage_params(sleep_time, run_time)
	#api.set_lpm_status(2)

SEND_TEMP = True
if SEND_TEMP:
	api.send_system_temp()
	
GET_OAP = False
if GET_OAP:
	set_day_night = oap_api.SetDayNight()
	night = set_day_night.android_auto_night_mode
else:
	night = False

GET_UPS = True
if GET_UPS:
	ver = api.get_firmware_ver()
	print("UPS firmware:", ver)
	
	if ver is None: print("RESET MCU" if api.restore_factory_defaults() == 1 else "FAILED TO RESET")

	temps = (api.get_input_temp(),    api.get_system_temp(),    api.get_battery_temp())
	volts = (api.get_input_voltage(), api.get_system_voltage(), api.get_battery_voltage())
	currs = (api.get_input_current(), api.get_system_current(), api.get_battery_current())
	powrs = (api.get_input_power(),   api.get_system_power(),   api.get_battery_power())
	lvls  = (api.get_battery_level(), api.get_battery_max_charge_level())
	
	dt_rtc = api.get_rtc_time(Definition.TIME_FORMAT_EPOCH)
	
	speed, capacity = api.get_fan_speed(), api.get_battery_design_capacity()
	
	health_fan, health_bat = "healthy" if api.get_fan_health() == 1 else "broken", api.get_battery_health()
	
	fan_auto = api.get_fan_automation()
	fan_mode = api.get_fan_mode()
else:
	temps = (0.0, 0.0, 0.0)
	volts = (0.0, 0.0, 0.0)
	currs = (0.0, 0.0, 0.0)
	powrs = (0.0, 0.0, 0.0)
	lvls = (0.0, 0.0)
	
	dt_rtc = datetime.datetime.fromtimestamp(int(0))
	
	speed, capacity = 0, 0
	fan_auto = [0, 0]
	
	health_fan, health_bat = "unk", 0
	fan_mode = -1

GET_GPS = True
if GET_GPS:
	gpsd.connect()
	packet = gpsd.get_current()
	
	gps_modes = dict()
	gps_modes[0] = "Invlid"
	gps_modes[1] = "No Fix"
	gps_modes[2] = "2D Fix"
	gps_modes[3] = "3D Fix"
	gps_mode = gps_modes[packet.mode]
	
	sat = packet.sats
	if packet.mode < 2:
		dt_gps = 0
	else:	
		dt_gps = datetime.datetime.strptime(packet.time[0:19], "%Y-%m-%dT%H:%M:%S")
		
	if packet.mode >= 2:
		gps_tim = dt_gps.timestamp()-time.timezone
		gps_lat = packet.lat
		gps_lon = packet.lon
		gps_spd = packet.hspeed
		gps_trk = packet.track
		gps_eps = packet.error['s']
		gps_ept = packet.error['t']
		gps_epx = packet.error['x']
		gps_epy = packet.error['y']
	else:
		gps_tim = 0
		gps_lat = float("nan")
		gps_lon = float("nan")
		gps_spd = 0
		gps_trk = 0
		gps_eps = 0
		gps_ept = 0
		gps_epx = 0
		gps_epy = 0
	
	if packet.mode >= 3:
		gps_alt = packet.alt
		gps_clm = packet.climb
		gps_ecp = packet.error['c']
		gps_epv = packet.error['v']
	else:
		gps_alt = float("nan")
		gps_clm = float("nan")
		gps_ecp = 0
		gps_epv = 0

	mode0 = (gps_mode, str("%3d" % sat), health_fan, health_bat)
	mode1 = (gps_lat, 0, speed, capacity)
	mode2 = (gps_lon, gps_epy, fan_mode)
	
	mode3 = (gps_alt, gps_epx, fan_auto[0], fan_auto[1])
	mode4 = (gps_spd, gps_epv)
	
else:
	mode0 = ("No GPS", 0, health_fan, health_bat)
	mode1 = (0, 0, speed, capacity)
	mode2 = (0, 0, fan_mode)
	mode3 = (0, 0, fan_auto[0], fan_auto[1])
	mode4 = (0, 0)
	
	gps_tim = 0
	gps_spd = 0
	gps_trk = 0
	gps_clm = 0
	gps_ept = 0
	
if GET_UPS:
	rtc_date = api.get_rtc_time(Definition.TIME_FORMAT_DATE)
	rtc_time = api.get_rtc_time(Definition.TIME_FORMAT_TIME)
else:
	rtc_date = "??"
	rtc_time = "??"

dt_sys = datetime.datetime.fromtimestamp(int(time.time()))
t = int(time.time())
print("|***** Input Sensors *****|**** System Sensors *****|**** Battery Sensors ****|")
print("|     Temp: %5.2f °C      |       Temp: %5.2f °C    |       Temp: %5.2f °C    |" % temps)
print("|  Voltage: %5.2f V       |    Voltage: %5.2f V     |    Voltage: %5.2f V     |" % volts)
print("|  Current: %5.2f A       |    Current: %5.2f A     |    Current: %5.2f A     |" % currs)
print("|    Power: %5.2f W       |      Power: %5.2f W     |      Power: %5.2f W     |" % powrs)
print("|********** GPS **********|********** Fan **********|  Level/Max:   %3d %%/%3d |" % lvls)
print("| Mode: %s  Vis:%3s   |     Health:  %7s    |     Health:   %3d %%     |" % mode0)
print("| Lat:%8.3f° epy:%3dm  |      Speed: %5d RPM   |   Capacity:  %4d mAh   |" % mode1)
print("| Lon:%8.3f° eox:%3dm  |       Mode: %5d       |                         |" % mode2)
print("| Alt: %7.1fm epv:%3dm  | Thresholds:[%3d,%3d] °C |                         |" % mode3)
print("| Spd: %5.1fm/S eps:%3dm/S|***** Sys Date Time *****|***** RTC Date Time *****|" % mode4)

epoch = (int(gps_tim), gps_ept, int(time.time()), dt_rtc)
print("| dt:%10s ept:%5sS|     Epoch :  %10s |     Epoch :  %10s |" % epoch)

line = (gps_trk, dt_sys.strftime("%Y-%m-%d"), rtc_date)
print("| Track: %5.0f°           |   -> date :  %10s |   -> date :  %10s |" % line)

line = (gps_clm, gps_ecp, dt_sys.strftime("%H:%M:%S"), rtc_time)
print("| Climb: %3.0fm/S ecp:%3dm/S|   -> time :    %8s |   -> time :    %8s |" % line)

line = ( dt_sys, datetime.datetime.fromtimestamp(dt_rtc))
print("|                         |  lc %19s |  lc %19s |"% line)

print("|*************************|*************************|*************************|")

SET_TIME = True	
if SET_TIME:
	if GET_GPS and (t < gps_tim or FORCE_GPS_SET):
		print("set using GPS time")
		packet = gpsd.get_current()		# Get the packet again for most current time
		if packet.time != "":
			dt_gps = datetime.datetime.strptime( \
				packet.time[0:19], "%Y-%m-%dT%H:%M:%S")
			gps_tim = dt_gps.timestamp()-time.timezone
			t = int(gps_tim)
			FORCE_RTC_SET = True
			FORCE_SYS_SET = True

	output_stream = os.popen('timedatectl status')
	output = output_stream.read()
	output_stream.close()
	
	if output.find("System clock synchronized: yes") != -1 and output.find("NTP service: active") != -1: 
		USE_SYS_TIME = True
	else:
		USE_SYS_TIME = False

	if (USE_SYS_TIME and math.fabs(t - dt_rtc) > 1) or FORCE_RTC_SET:
		print("sys -> RTC")
		api.set_rtc_time(t)
		print("api.set_rtc_time(int(time.time()+time.timezone))")

	if math.fabs(t - dt_rtc) > 1 or FORCE_SYS_SET:
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

if api.get_working_mode() == Definition.BATTERY_POWERED and api.get_input_power() <= 0.:
#	
#	if subprocess.call(["systemctl", "is-active", "--quiet", "shutdown_edm.service"]) == 0 \
#	or subprocess.call(["systemctl", "start", "shutdown_edm.service"]) == 0:
#		print("EDM service active")
#	else:
#		if REQUIRE_EDM_FOR_SHUTDOWN:
#			print("EDM service not running and is required. Aborting shutdown process")
#			exit()
			
	if ENABLE_SHUTDOWN:
		print("Result removing all Scheduled Event: " + str(api.remove_all_scheduled_events(200)))
			
		print("Powering down")
		
		"""
		level, status = 50, 2
		api.set_safe_shutdown_battery_level(level)
		api.set_safe_shutdown_status(status)
		"""

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
			print("Sending shutdown command")
			#os.system("sleep 1 && sudo shutdown -h now")
			os.system("sleep 1 && reboot")
		else:
			print("Shutdown command disabled")

	if BLANK_LCD:
		os.system("vcgencmd set_backlight 0 0")
		os.system("vcgencmd display_power 0 0")
	else:
		print("Keeping LCD on for now")
		
print("Good byte")
exit()
