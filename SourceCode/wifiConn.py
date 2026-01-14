import time
import network

WIFI_SSID = 'IoT@UMT'
WIFI_PASSWORD = 'i00t@UMT'

def is_connected():
    wlan = network.WLAN(network.STA_IF)
    return wlan.isconnected()

def connect_to_wifi(timeout=10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        start_time = time.time()
        while not wlan.isconnected():
            if time.time() - start_time > timeout:
                print('Connection timed out.')
                return False
            time.sleep(1)
    
    print('Network connected:', wlan.ifconfig())
    return True 

# Disconnect from Wi-Fi
def disconnect_from_wifi():
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        wlan.disconnect()
        print('Disconnected from Wi-Fi.')
    else:
        print('No active Wi-Fi connection to disconnect.')
    wlan.active(False)
    print('Wi-Fi interface deactivated.')

