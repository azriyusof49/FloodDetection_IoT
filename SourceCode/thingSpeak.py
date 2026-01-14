import urequests
import ujson
THINGSPEAK_WRITE_API_KEY = "API_KEY"  # Replace with your API key

# LED Control Channel Configuration (NEW)
THINGSPEAK_CHANNEL_ID = "CHANNEL_ID"    # Replace channel ID
THINGSPEAK_READ_API_KEY = "API_KEY" 

# ThingSpeak API URL
API_URL = "http://api.thingspeak.com"
    
def write_thingspeak_data(waterPercent, waterCm, rate, RainADC, humidity, temperature):
    get_url = API_URL + "/update?api_key=" + THINGSPEAK_WRITE_API_KEY + "&field1={}&field2={}&field3={}&field4={}&field5={}&field6={}".format(
        waterPercent, waterCm, rate, RainADC, humidity, temperature)
    print("Sending data to ThingSpeak...")
    try:
        response = urequests.get(get_url)
        if response.status_code == 200:
            print("Data sent successfully.")
        else:
            print("Failed to send data. HTTP Error:", response.status_code)
        response.close()
    except Exception as e:
        print("Error sending data to ThingSpeak:", e)


