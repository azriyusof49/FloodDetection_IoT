from machine import Pin, ADC, SoftI2C
from utime import sleep, ticks_ms, ticks_diff
from hcsr04 import HCSR04
import dht
import wifiConn, thingSpeak, calculateRain
from pico_i2c_lcd import I2cLcd


# -----------------------------
# CONFIG
# -----------------------------
TRIG_PIN = 1
ECHO_PIN = 0
DHT_PIN  = 15

TANK_DEPTH_CM = 30         # adjust to your tank depth
ULTRASONIC_OFFSET_CM = 35   # adjust to your sensor installation height

POST_INTERVAL_S = 1200           # ThingSpeak free tier: >= 20Min
WIFI_RETRY_MS = 10_000
DHT_RETRY = 3

RAIN_ADC_PIN = 26              # GP26 ADC0
RAIN_SAMPLES = 5               # moving average window

# LCD DISPLAY
I2C = SoftI2C(sda=Pin(12), scl=Pin(13), freq=400000)
ADDRESS = 0x27
DISPLAY = I2cLcd(I2C, ADDRESS, 2, 16)

# -----------------------------
# INIT HARDWARE
# -----------------------------
led = Pin(16, Pin.OUT)
ultra = HCSR04(trigger_pin=TRIG_PIN, echo_pin=ECHO_PIN)
rain_adc = ADC(Pin(RAIN_ADC_PIN))
dht_sensor = dht.DHT11(Pin(DHT_PIN))

water_state = None
last_wifi_try = 0

# Moving average buffer for rain ADC (0..1023)
rain_buf = [0] * RAIN_SAMPLES
rain_i = 0
rain_count = 0

LCD_WIDTH = 16

def lcd_safe(func, *args):
    try:
        func(*args)
    except OSError:
        pass

def scroll_text(line, row=0, delay=0.3):
    if len(line) <= LCD_WIDTH:
        lcd_safe(DISPLAY.move_to, 0, row)
        lcd_safe(DISPLAY.putstr, line)
        return

    padded = line + " " * LCD_WIDTH

    for i in range(len(padded) - LCD_WIDTH + 1):
        lcd_safe(DISPLAY.move_to, 0, row)
        lcd_safe(DISPLAY.putstr, padded[i:i + LCD_WIDTH])
        sleep(delay)

def displayAlert(msg):
    try:
        DISPLAY.clear()
        scroll_text(msg, row=0)
    except OSError as e:
        print("LCD TURN OFF", e)

def displayInfo(temp, hum, level):
    try:
        DISPLAY.clear()

        line1 = f"Temp:{temp}C Level:"
        line2 = f"Hum:{hum}%   {level:.1f}cm"

        scroll_text(line1, row=0)
        scroll_text(line2, row=1)

    except OSError as e:
        print("LCD TURN OFF", e)


def blink(times=1, on_ms=80, off_ms=80):
    for _ in range(times):
        led.on()
        sleep(on_ms / 1000)
        led.off()
        sleep(off_ms / 1000)

def ensure_wifi():
    """Reconnect WiFi with cooldown."""
    global last_wifi_try
    if wifiConn.is_connected():
        return True

    now = ticks_ms()
    if ticks_diff(now, last_wifi_try) < WIFI_RETRY_MS:
        print("WiFi not connected. Reconnecting...")
        displayAlert("WiFi not connected. Reconnecting...")
        return False
    last_wifi_try = now
    return wifiConn.connect_to_wifi()

def read_dht_with_retry():
    for _ in range(DHT_RETRY):
        try:
            dht_sensor.measure()
            return dht_sensor.temperature(), dht_sensor.humidity()
        except Exception:
            sleep(0.15)
    return None, None

def read_rain_adc_avg():
    """Read rain ADC and return averaged 0..1023 value (less noise)."""
    global rain_i, rain_count
    adc1023 = rain_adc.read_u16() >> 6  # 0..1023

    rain_buf[rain_i] = adc1023
    rain_i = (rain_i + 1) % RAIN_SAMPLES
    if rain_count < RAIN_SAMPLES:
        rain_count += 1

    return sum(rain_buf[:rain_count]) // rain_count

def run_once():
    global water_state

    # 1) Read sensors
    rainADC = read_rain_adc_avg()
    temperature, humidity = read_dht_with_retry()
    distance = ultra.distance_cm()
    

    # If DHT fails, keep last valid or send 0
    if temperature is None or humidity is None:
        temperature, humidity = 0, 0

    # 2) Water metrics (your existing function)
    # NOTE: This function likely triggers the sensor internally.
    waterPercent, waterCm, rate, water_state = calculateRain.get_water_metrics(
        trig_pin=TRIG_PIN,
        echo_pin=ECHO_PIN,
        tank_depth_cm=TANK_DEPTH_CM,
        sensor_offset_cm=ULTRASONIC_OFFSET_CM,
        state=water_state,
        distance=distance
    )

    # 3) Send to ThingSpeak (only if online)
    if ensure_wifi():
        thingSpeak.write_thingspeak_data(
            waterPercent, waterCm, rate, rainADC, humidity, temperature
        )
        print(f"Temp: {temperature}°C  Hum: {humidity}%  RainADC(avg): {rainADC}")
        print(f"Water: {waterCm:.1f} cm | {waterPercent:.1f}% | Rate: {rate:.2f} cm/min | Distance: {distance:.1f} cm")
        displayInfo(temperature, humidity, waterCm)
        blink(2, on_ms=50, off_ms=50)
    else:
        print("Offline. Skipping ThingSpeak update.")
        blink(1, on_ms=30, off_ms=30)

print("Initializing system...")
displayAlert("Initializing system...")
sleep(2)
ensure_wifi()
blink(5, on_ms=40, off_ms=40)

try:
    while True:
        run_once()
        print("=" * 50)
        sleep(POST_INTERVAL_S)
except KeyboardInterrupt:
    displayAlert("Terminating...")
    sleep(2)
    DISPLAY.clear()
    print("Terminating...")
finally:
    led.off()
    print("Finished.")
