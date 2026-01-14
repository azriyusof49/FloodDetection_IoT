from machine import Pin, time_pulse_us
import utime
from hcsr04 import HCSR04

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


def get_water_metrics(trig_pin: int,
                      echo_pin: int,
                      tank_depth_cm: float,
                      sensor_offset_cm: float = 0.0,
                      state: dict | None = None,
                      distance: float = 0.0):
    """
    Returns (waterPercent, waterCm, rate_cm_per_min, updated_state)

    - tank_depth_cm: total tank depth from sensor reference to bottom (cm)
    - sensor_offset_cm: calibration offset (cm). Use if sensor isn't exactly at the top reference.
    - state: pass back the returned state to compute rate over time.
    """

    if state is None:
        state = {"last_cm": None, "last_t_ms": None}

    trig = Pin(trig_pin, Pin.OUT)
    echo = Pin(echo_pin, Pin.IN)

    # 1) Read distance from sensor to water surface
    #distance_cm = measure_distance_cm(trig, echo) + sensor_offset_cm
    distance -= sensor_offset_cm
    print(distance)

    # Clamp distance to sane range
    if distance < 0:
        distance = 0

    # 2) Convert to water height (cm) and percent
    waterCm = tank_depth_cm - distance
    if waterCm < 0:
        waterCm = 0.0
    waterPercent = (waterCm / tank_depth_cm) * 100 if tank_depth_cm > 0 else 0

    # Clamp percent
    if waterPercent < 0: waterPercent = 0
    if waterPercent > 100: waterPercent = 100

    # 3) Rate (cm/min)
    now_ms = utime.ticks_ms()
    rate = 0.0

    if state["last_cm"] is not None and state["last_t_ms"] is not None:
        dt_ms = utime.ticks_diff(now_ms, state["last_t_ms"])
        if dt_ms > 0:
            dcm = waterCm - state["last_cm"]
            rate = (dcm / (dt_ms / 60000.0))  # cm per minute

    # Update state
    state["last_cm"] = waterCm
    state["last_t_ms"] = now_ms

    return waterPercent, waterCm, rate, state
