import pyowm
import socket
import asyncio
import time
import logging

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")

class Weather(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)

    def get_current_weather(self, city, key):
        owm = pyowm.OWM(key)
        observation = owm.weather_at_place('{0}, us'.format(city))
        return observation.get_weather().to_JSON()

    def get_current_temperature(self, city, key):
        owm = pyowm.OWM(key)
        observation = owm.weather_at_place('{0}, us'.format(city))
        print(observation)
        weather = observation.get_weather()
        print(weather)
        print(weather.get_temperature('fahrenheit')['temp'])
        return weather.get_temperature('fahrenheit')['temp']
