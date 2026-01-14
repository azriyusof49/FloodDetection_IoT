#---------------------
# FSKM UMT
# CSM3313 IoT
# MicroPython with Pico W lesson by Cikgu Fadzli
# HC-SR04 Ultrasonic Distance Sensor
#---------------------
# Required library:
# 1. hcsr04.py - Place this file in the same directory or in /lib folder
#---------------------
import utime
from hcsr04 import HCSR04
from machine import Pin, time_pulse_us
import time

# Initialize the HC-SR04 sensor
# trigger_pin=7 (GPIO7), echo_pin=6 (GPIO6)
sonar = HCSR04(trigger_pin=1, echo_pin=0)

trig = Pin(1, Pin.OUT)
echo = Pin(0, Pin.IN)

def measure_distance_cm(trig: Pin, echo: Pin) -> float:
    """
    Measure distance (cm) using HC-SR04.
    Returns distance in cm.
    """
    # Trigger a 10us pulse
    trig.low()
    utime.sleep_us(2)
    trig.high()
    utime.sleep_us(10)
    trig.low()

    # Measure echo pulse (timeout 30ms ~ 5m)
    duration = time_pulse_us(echo, 1, 30000)

    # duration is in microseconds
    # Sound speed ~343 m/s => 0.0343 cm/us
    # Divide by 2 because it goes out and back
    distance_cm = (duration * 0.0343) / 2
    return distance_cm

while True:
    try:
        distance_cm = measure_distance_cm(trig, echo)
        print("Measured Distance: {:.2f} cm".format(distance_cm))
    except OSError as e:
        print("Retrying! Error:", e)
    time.sleep(0.1)