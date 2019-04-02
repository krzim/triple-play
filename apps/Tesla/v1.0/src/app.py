import apps.Tesla.teslajson as teslajson
import socket
import asyncio
import time
import logging

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")

class Tesla(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)

    def get_mobile_access(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return bool(vehicle.data_request('mobile_enabled')['response'])

    # Functions relating to vehicle charge state
    def get_charge_state_all(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return vehicle.data_request('charge_state')

    def get_charging_state(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return (vehicle.data_request('charge_state'))['charging_state']

    def get_charge_to_max_range(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return bool((vehicle.data_request('charge_state'))['charge_to_max_range'])

    def get_max_range_charge_counter(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return int((vehicle.data_request('charge_state'))['max_range_charge_counter'])

    def get_fast_charger_present(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return bool((vehicle.data_request('charge_state'))['fast_charger_present'])

    def get_battery_range(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return float((vehicle.data_request('charge_state'))['battery_range'])

    def get_est_battery_range(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return float((vehicle.data_request('charge_state'))['est_battery_range'])

    def get_ideal_battery_range(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return float((vehicle.data_request('charge_state'))['ideal_battery_range'])

    def get_battery_level(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return (vehicle.data_request('charge_state'))['battery_level']

    def get_battery_current(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return (vehicle.data_request('charge_state'))['battery_current']

    def get_charger_voltage(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return float((vehicle.data_request('charge_state'))['charger_voltage'])

    def get_charger_pilot_current(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return float((vehicle.data_request('charge_state'))['charger_pilot_current'])

    def get_charger_actual_current(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return float((vehicle.data_request('charge_state'))['charger_actual_current'])

    def get_charger_power(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return float((vehicle.data_request('charge_state'))['charger_power'])

    def get_time_to_full_charge(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return (vehicle.data_request('charge_state'))['time_to_full_charge']

    def get_charge_rate(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return float((vehicle.data_request('charge_state'))['charge_rate'])

    def get_charge_port_door_open(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return bool((vehicle.data_request('charge_state'))['charge_port_door_open'])

    # Functions relating to vehicle climate state
    def get_climate_state_all(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')

        return vehicle.data_request('climate_state')

    def get_inside_temp(self, username, password):
        return float((vehicle.data_request('climate_state'))['inside_temp'])

    def get_outside_temp(self, username, password):
        return float((vehicle.data_request('climate_state'))['outside_temp'])

    def get_driver_temp_setting(self, username, password):
        return float((vehicle.data_request('climate_state'))['driver_temp_setting'])

    def get_passenger_temp_setting(self, username, password):
        return float((vehicle.data_request('climate_state'))['passenger_temp_setting'])

    def get_is_auto_conditioning_on(self, username, password):
        return bool((vehicle.data_request('climate_state'))['is_auto_conditioning_on'])

    def get_is_front_defroster_on(self, username, password):
        return bool((vehicle.data_request('climate_state'))['is_front_defroster_on'])

    def get_is_rear_defroster_on(self, username, password):
        return bool((vehicle.data_request('climate_state'))['is_rear_defroster_on'])

    def get_fan_status(self, username, password):
        return int((vehicle.data_request('climate_state'))['fan_status'])

    # Functions relating to vehicle driving and position
    def get_driving_and_position_all(self, username, password):
        return vehicle.data_request('drive_state')

    def get_shift_state(self, username, password):
        return (vehicle.data_request('driver_state'))['shift_state']

    def get_speed(self, username, password):
        return float((vehicle.data_request('driver_state'))['speed'])

    def get_latitude(self, username, password):
        return float((vehicle.data_request('driver_state'))['latitude'])

    def get_longitude(self, username, password):
        return float((vehicle.data_request('driver_state'))['longitude'])

    def get_heading(self, username, password):
        return int((vehicle.data_request('driver_state'))['heading'])

    # def get_gps_as_of(self, username, password):
    #     return int((vehicle.data_request('driver_state'))['gps_as_of'])

    # Functions relating to vehicle GUI
    def get_gui_settings_all(self, username, password):
        return vehicle.data_request('gui_settings')

    def get_gui_distance_units(self, username, password):
        return (vehicle.data_request('gui_settings'))['gui_distance_units']

    def get_gui_temperature_units(self, username, password):
        return (vehicle.data_request('gui_settings'))['gui_temperature_units']

    def get_gui_charge_rate_units(self, username, password):
        return (vehicle.data_request('gui_settings'))['gui_charge_rate_units']

    def get_gui_24_hour_time(self, username, password):
        return bool((vehicle.data_request('gui_settings'))['gui_24_hour_time'])

    def get_gui_range_display(self, username, password):
        return (vehicle.data_request('gui_settings'))['gui_range_display']

    # Functions relating to vehicle state (mainly physical)
    def get_vehicle_state_all(self, username, password):
        return vehicle.data_request('vehicle_state')

    def get_driver_front_door(self, username, password):
        return bool((vehicle.data_request('vehicle_state'))['df'])

    def get_driver_rear_door(self, username, password):
        return bool((vehicle.data_request('vehicle_state'))['dr'])

    def get_passenger_front_door(self, username, password):
        return bool((vehicle.data_request('vehicle_state'))['pf'])

    def get_passenger_rear_door(self, username, password):
        return bool((vehicle.data_request('vehicle_state'))['pr'])

    def get_front_trunk(self, username, password):
        return bool((vehicle.data_request('vehicle_state'))['ft'])

    def get_rear_trunk(self, username, password):
        return bool((vehicle.data_request('vehicle_state'))['rt'])

    def get_car_firmware_version(self, username, password):
        return (vehicle.data_request('vehicle_state'))['car_version']

    def get_locked(self, username, password):
        return bool((vehicle.data_request('vehicle_state'))['locked'])

    def get_sunroof_installed(self, username, password):
        return bool((vehicle.data_request('vehicle_state'))['sun_roof_installed'])

    def get_sunroof_state(self, username, password):
        return (vehicle.data_request('vehicle_state'))['sun_roof_state']

    def get_sunroof_percent_open(self, username, password):
        return float((vehicle.data_request('vehicle_state'))['sun_roof_percent_open'])

    def get_dark_rims(self, username, password):
        return bool((vehicle.data_request('vehicle_state'))['dark_rims'])

    def get_wheel_type(self, username, password):
        return (vehicle.data_request('vehicle_state'))['wheel_type']

    def get_has_spoiler(self, username, password):
        return bool((vehicle.data_request('vehicle_state'))['has_spoiler'])

    def get_roof_color(self, username, password):
        return (vehicle.data_request('vehicle_state'))['roof_color']

    def get_perf_config(self, username, password):
        return (vehicle.data_request('vehicle_state'))['perf_config']

    def wake_up(self, username, password):
        return bool(vehicle.wake_up()['result'])

    def set_valet_mode(self, on, pin, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        # Args: boolean to disable or enable valet mode 'on', and 4 digit PIN to unlock the car 'password'
        data = {'mode': on}
        if pin is not None:
            data['password'] = pin
        return bool(vehicle.command('set_valet_mode', data=data)['result'])

    def reset_valet_pin(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        return bool(vehicle.command('reset_valet_pin'))

    def open_charge_port(self, username, password):
        return bool(vehicle.command('charge_port_door_open')['result'])

    def set_charge_limit_std(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        return bool(vehicle.command('charge_standard')['result'])

    def set_charge_limit_max_range(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        return bool(vehicle.command('charge_max_range')['result'])

    def set_charge_limit(self, limit):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        # Args: int percentage value for charge limit 'limit_value'
        data = {"limit_value": limit}
        return bool(vehicle.command('set_charge_limit', data=data)['result'])

    def start_charging(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        return bool(vehicle.command('charge_start')['result'])

    def stop_charging(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        return bool(vehicle.command('charge_stop')['result'])

    def flash_lights(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        return bool(vehicle.command('flash_lights')['result'])

    def honk_horn(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        return bool(vehicle.command('honk_horn')['result'])

    def unlock_doors(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        return bool(vehicle.command('door_unlock')['result'])

    def lock_doors(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        return bool(vehicle.command('door_lock')['result'])

    def set_temperature(self, driver_deg_c, passenger_deg_c):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        # Args: int temp for driver's side in celsius driver_degC, int temp for passenger's side in celsius pass_degC
        data = {"driver_degC": driver_deg_c, "pass_degC": passenger_deg_c}
        return bool(vehicle.command('set_temps', data=data)['result'])

    def start_hvac_system(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        return bool(vehicle.command('auto_conditioning_start')['result'])

    def stop_hvac_system(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        return bool(vehicle.command('auto_conditioning_stop')['result'])

    def move_pano_roof(self, state, percent):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        # Args: desired state of pano roof (open, close, comfort, vent) 'state', optional int percentage to move
        # the roof to 'percent'
        data = {"state": state, "percent": percent}
        return bool(vehicle.command('sun_roof_control', data=data)['result'])

    def remote_start(self, username, password):
        connection = teslajson.Connection(username, password)
        try:
            vehicle = connection.vehicles[0]
        except IndexError:
            logger.error('This account has no tesla vehicles')
        # Args: password to the account
        return bool(vehicle.command('remote_start_drive',
                                         data={"password": device.get_encrypted_field('password')})['result'])
