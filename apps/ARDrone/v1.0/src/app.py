from apps.ARDrone.libardrone import libardrone
import time
from time import sleep
import socket
import asyncio
import logging

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")

class ARDrone(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)

    def takeoff(self):
        """Make the drone takeoff."""
        libardrone.ARDrone().takeoff()
        return "Success"

    def land(self):
        """Make the drone land."""
        libardrone.ARDrone().land()
        return "Success"

    def __timed_execute(self, time):
        """ sleep for a given amount of time if time is > 0. Time is given im milliseconds"""
        if time >= 0:
            sleep(time/1000.)

    def hover(self, millisec):
        """Make the drone hover."""
        libardrone.ARDrone().at(libardrone.at_pcmd, False, 0, 0, 0, 0)
        self.__timed_execute(millisec)
        return "Success"

    def move_left(self, speed, millisec):
        """Make the drone move left."""
        libardrone.ARDrone().at(libardrone.at_pcmd, True, -speed/10., 0, 0, 0)
        self.__timed_execute(millisec)
        return "Success"

    def move_right(self, speed, millisec):
        """Make the drone move right."""
        libardrone.ARDrone().at(libardrone.at_pcmd, True, speed/10., 0, 0, 0)
        self.__timed_execute(millisec)
        return "Success"

    def move_up(self, speed, millisec):
        """Make the drone rise upwards."""
        libardrone.ARDrone().at(libardrone.at_pcmd, True, 0, 0, speed/10., 0)
        self.__timed_execute(millisec)
        return "Success"

    def move_down(self, speed, millisec):
        """Make the drone decent downwards."""
        libardrone.ARDrone().at(libardrone.at_pcmd, True, 0, 0, -speed/10., 0)
        self.__timed_execute(millisec)
        return "Success"

    def move_forward(self, speed, millisec):
        """Make the drone move forward."""
        libardrone.ARDrone().at(libardrone.at_pcmd, True, 0, -speed/10., 0, 0)
        self.__timed_execute(millisec)

    def move_backward(self, speed, millisec):
        """Make the drone move backwards."""
        libardrone.ARDrone().at(libardrone.at_pcmd, True, 0, speed/10., 0, 0)
        self.__timed_execute(millisec)
        return "Success"

    def turn_left(self, speed, millisec):
        """Make the drone rotate left."""
        libardrone.ARDrone().at(libardrone.at_pcmd, True, 0, 0, 0, -speed/10.)
        self.__timed_execute(millisec)
        return "Success"

    def turn_right(self, speed, millisec):
        """Make the drone rotate right."""
        libardrone.ARDrone().at(libardrone.at_pcmd, True, 0, 0, 0, speed/10.)
        self.__timed_execute(millisec)
        return "Success"

    def reset(self):
        """Toggle the drone's emergency state."""
        libardrone.ARDrone().reset()
        return "Success"

    def trim(self):
        """Flat trim the drone."""
        libardrone.ARDrone().at(libardrone.at_ftrim)
        return "Success"

    def set_speed(self, speed):
        """Set the drone's speed.

        Valid values are ints from [0.1]
        """
        libardrone.ARDrone().speed = speed/10.
        return "Success"

    def move(self, left_right_tilt, front_back_tilt, vertical_speed, angular_speed, millisec):
        """Makes the drone move (translate/rotate).

       Parameters:
       lr -- left-right tilt: float [-1..1] negative: left, positive: right
       rb -- front-back tilt: float [-1..1] negative: forwards, positive:
            backwards
       vv -- vertical speed: float [-1..1] negative: go down, positive: rise
       va -- angular speed: float [-1..1] negative: spin left, positive: spin 
            right"""
        libardrone.ARDrone().at(libardrone.at_pcmd,
                      True,
                      left_right_tilt,
                      front_back_tilt,
                      vertical_speed,
                      angular_speed)
        self.__timed_execute(millisec)
        return "Success"

    def halt(self):
        libardrone.ARDrone().halt()
        return "Success"

    def get_image(self):
        return libardrone.ARDrone().image

    def get_battery(self):
        return str(libardrone.ARDrone().navdata.get(0, dict()).get('battery', 0))

    def get_theta(self):
        return str(libardrone.ARDrone().navdata.get(0, dict()).get('theta', 0))

    def get_phi(self):
        return str(libardrone.ARDrone().navdata.get(0, dict()).get('phi', 0))

    def get_psi(self):
        return str(libardrone.ARDrone().navdata.get(0, dict()).get('psi', 0))

    def get_altitude(self):
        return str(libardrone.ARDrone().navdata.get(0, dict()).get('altitude', 0))

    def get_velocity_x(self):
        return str(libardrone.ARDrone().navdata.get(0, dict()).get('vx', 0))

    def get_velocity_y(self):
        return str(libardrone.ARDrone().navdata.get(0, dict()).get('vy', 0))

    def get_velocity_z(self):
        return str(libardrone.ARDrone().navdata.get(0, dict()).get('vz', 0))

    def shutdown(self):
        libardrone.ARDrone().land()
        libardrone.ARDrone().halt()
        return "Success"
