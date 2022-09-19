import time
import sys
import os

sys.path.append('./')

from power_api import SixfabPower

api = SixfabPower()

if __name__ == "__main__":

#    api.restore_factory_defaults(4000)

    slow_threshold, fast_threshold, mode = 40, 60, 3
    print(str(api.set_fan_automation(slow_threshold, fast_threshold, timeout=200)))
    print(str(api.set_fan_mode(mode)))
    
    level, status = 60, 2
    api.set_safe_shutdown_battery_level(level)
    api.set_safe_shutdown_status(status)

    level, capacity = 95, 3000
    api.set_battery_max_charge_level(level)
    api.set_battery_design_capacity(capacity)

    status = 1
    api.set_lpm_status(status, 1000)

    #status = 1
    #api.set_edm_status(status)

    #set_watchdog_status(status)
    #set_watchdog_interval(interval)

    #set_rgb_animation(anim_type, color, speed)
    
    #set_battery_separation_status(status)

    #set_rtc_time(timestamp)

    #set_power_outage_params(sleep_time, run_time)
    #set_power_outage_event_status(status)

    #set_end_device_alive_threshold(threshold)
    
