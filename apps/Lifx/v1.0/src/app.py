
import requests

import socket
import asyncio
import time
import logging

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")

class Lifx(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)

    def __api_url(self, endpoint, name, act_on_all=False):
        base_url = 'https://api.lifx.com/v1/lights'
        if act_on_all:
            return '{0}/all/{2}'
        else:
            return '{0}/label:{1}/{2}'.format(base_url, name, endpoint)

    def list_lights(self, token):
        headers = {"Authorization": "Bearer {0}".format(token)}
        response = requests.get(self.__api_url('', act_on_all=True), headers=headers)
        return response.text

    def set_state(self, power, color, brightness, duration, infrared, token, name):
        """
        Sets the state of the light
        power: on or off
        color: color to set the lights to
        brightness: int from 0 to 1
        duration: seconds for the action to last
        infrared: 0 to 1. maximum brightness of infrared channel
        """
        headers = {"Authorization": "Bearer {0}".format(token)}
        payload = {"duration": duration}
        if power is not None:
            payload['power'] = power
        if color is not None:
            payload['color'] = color
        if brightness is not None:
            payload['brightness'] = brightness
        if infrared is not None:
            payload['duration'] = duration
        response = requests.put(self.__api_url('state'.format(name)), data=payload, headers=headers)
        time.sleep(duration)
        return response.text

    def toggle_power(self, duration, wait, token, name):
        """
        Sets the state of the light
        duration: seconds for the action to last
        """
        headers = {"Authorization": "Bearer {0}".format(token)}
        payload = {"duration": duration}
        response = requests.post(self.__api_url('toggle'.format(name)), data=payload, headers=headers)
        if wait:
            time.sleep(duration)
        return response.text


    def breathe_effect(self, color, from_color, period, cycles, persist, power_on, peak, wait, token, name):
        """
        Slowly fades between two colors
        color: color to use for the breathe effect
        from_color: color to start the breathe effect from
        period: Time in seconds between cycles
        cycles: Number of times to repeat the effect
        persist: If false set teh light back to its previous value when effect ends. Else leave at last effect
        power_on: If true, turn on the light if not already on
        peak: where in the period the target color is at its maximum. Between 0 and 10
        """
        headers = {"Authorization": "Bearer {0}".format(token)}
        payload = {"color": color,
                   "period": period,
                   "cycles": cycles,
                   "persist": persist,
                   "power_on": power_on,
                   "peak": peak}
        if from_color is not None:
            payload['from_color'] = from_color
        response = requests.post(self.__api_url('effects/breathe'.format(name)),
                                 data=payload,
                                 headers=headers)
        if wait:
            time.sleep(period * cycles)
        return response.text


    def pulse_effect(self, color, from_color, period, cycles, persist, power_on, wait, token):
        """
        Quickly flashes between two colors
        color: color to use for the breathe effect
        from_color: color to start the breathe effect from
        period: Time in milliseconds between cycles
        cycles: Number of times to repeat the effect
        persist: If false set teh light back to its previous value when effect ends. Else leave at last effect
        power_on: If true, turn on the light if not already on
        """
        headers = {"Authorization": "Bearer {0}".format(token)}
        payload = {"color": color,
                   "period": period,
                   "cycles": cycles,
                   "persist": persist,
                   "power_on": power_on}
        if from_color is not None:
            payload['from_color'] = from_color
        response = requests.post(self.__api_url('effects/pulse'),
                                 data=payload,
                                 headers=headers)
        if wait:
            time.sleep(period * cycles)
        return response.text
