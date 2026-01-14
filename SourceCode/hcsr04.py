"""
MicroPython HC-SR04 Ultrasonic Distance Sensor Library
Author: Adapted for MicroPython
Description: Driver for HC-SR04 ultrasonic sensor
Range: 2cm to 4m
"""

import utime
from machine import Pin, time_pulse_us


class HCSR04:
    """
    Driver to use the ultrasonic sensor HC-SR04.
    The sensor range is between 2cm and 4m.
    """
    
    def __init__(self, trigger_pin, echo_pin, echo_timeout_us=500*2*30):
        """
        Initialize the HC-SR04 sensor.
        
        Args:
            trigger_pin: GPIO pin number for trigger (output)
            echo_pin: GPIO pin number for echo (input)
            echo_timeout_us: Timeout in microseconds to listen to echo pin.
                           By default is based on sensor limit range (4m)
        """
        self.echo_timeout_us = echo_timeout_us
        
        # Init trigger pin (output)
        self.trigger = Pin(trigger_pin, Pin.OUT)
        self.trigger.value(0)

        # Init echo pin (input)
        self.echo = Pin(echo_pin, Pin.IN)

    def _send_pulse_and_wait(self):
        """
        Send the pulse to trigger and listen on echo pin.
        We use the method `machine.time_pulse_us()` to get the microseconds until the echo is received.
        
        Returns:
            int: Pulse time in microseconds
            
        Raises:
            OSError: If sensor is out of range or timeout occurs
        """
        self.trigger.value(0)  # Stabilize the sensor
        utime.sleep_us(5)
        self.trigger.value(1)
        # Send a 10us pulse
        utime.sleep_us(10)
        self.trigger.value(0)
        
        try:
            pulse_time = time_pulse_us(self.echo, 1, self.echo_timeout_us)
            return pulse_time
        except OSError as ex:
            if ex.args[0] == 110:  # 110 = ETIMEDOUT
                raise OSError('Out of range')
            raise ex

    def distance_mm(self):
        """
        Get the distance in millimeters without floating point operations.
        
        Returns:
            int: Distance in millimeters
        """
        pulse_time = self._send_pulse_and_wait()

        # To calculate the distance we get the pulse_time and divide it by 2 
        # (the pulse travels the distance twice) and by 29.1 because
        # the sound speed in air (343.2 m/s), that is equivalent to
        # 0.34320 mm/us that is 1mm each 2.91us
        # pulse_time // 2 // 2.91 -> pulse_time // 5.82 -> pulse_time * 100 // 582 
        mm = pulse_time * 100 // 582
        return mm

    def distance_cm(self):
        """
        Get the distance in centimeters with floating point operations.
        
        Returns:
            float: Distance in centimeters
        """
        pulse_time = self._send_pulse_and_wait()

        # To calculate the distance we get the pulse_time and divide it by 2 
        # (the pulse travels the distance twice) and by 29.1 because
        # the sound speed in air (343.2 m/s), that is equivalent to
        # 0.34320 mm/us that is 1mm each 2.91us
        cms = (pulse_time / 2) / 29.1
        return cms
        
    def distance_inches(self):
        """
        Get the distance in inches with floating point operations.
        
        Returns:
            float: Distance in inches
        """
        return self.distance_cm() / 2.54