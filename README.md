# FloodDetection IoT

**Project Overview**
This project is a simple IoT flood detection system using a Raspberry Pi Pico W. It includes a web dashboard, microcontroller code (for Pico W), and server/backend scripts if needed. The repository contains the dashboard (`index.html`, `styles.css`) and a `SourceCode` folder with the Pico W scripts.

> Note: This README assumes you are using a Pico W and may need to adjust file names or code paths based on the files in the `SourceCode` folder.

---

## Hardware Requirements

* Raspberry Pi Pico W
* Water level sensor / float sensor / ultrasonic sensor (e.g., HC-SR04)
* Buzzer / LED (for alerts)
* Breadboard, jumper wires, power supply (3.3V)

## Software Requirements

* Git
* Web browser to open the dashboard
* Python 3 (for running a local server if needed) — `python3 -m http.server`
* If a backend is used (Flask / Node.js), install required dependencies (Python example: `flask`, `paho-mqtt`)
* Thonny or uPyCraft for Pico W MicroPython scripts
* MQTT broker (e.g., Mosquitto) if using MQTT protocol

---

## Installation and Setup

### 1) Clone the repository

```bash
git clone https://github.com/azriyusof49/FloodDetection_IoT.git
cd FloodDetection_IoT
```

### 2) Check the repo structure

Open the `SourceCode` folder and examine the scripts. Adjust the instructions below according to the code type.

### 3A) Dashboard only (HTML/CSS/JS)

1. Open `index.html` in a browser directly or run a simple Python server:

```bash
# Python 3
python3 -m http.server 8000
```

2. Navigate to `http://localhost:8000` to view the dashboard.

### 3B) Backend server (Python/Flask)

1. (Optional) Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate    # Windows PowerShell
```

2. Install dependencies if `requirements.txt` exists:

```bash
pip install -r requirements.txt
```

3. Run the server (example):

```bash
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```

Then open `http://localhost:5000`.

### 4) MQTT Broker Setup (if using MQTT)

* Install Mosquitto:

```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

* Update broker address, port, and topic in the Pico W script.

### 5) Upload code to Pico W

1. Open Thonny.
2. Connect Pico W via USB.
3. Open the `.py` script from `SourceCode`.
4. Update WiFi credentials, MQTT broker info, and topics.
5. Save the script to Pico W (File -> Save As -> Raspberry Pi Pico).

### 6) Test the system

1. Power on the Pico W and sensors. Monitor the output in Thonny's shell.
2. If using MQTT, subscribe to the topic using `mosquitto_sub`:

```bash
mosquitto_sub -h localhost -t "flood/topic" -v
```

3. Open the dashboard to view real-time sensor readings.

---

## Configuration Example

Create `config.example.json`:

```json
{
  "wifi_ssid": "YOUR_WIFI_SSID",
  "wifi_password": "YOUR_WIFI_PASSWORD",
  "mqtt_broker": "192.168.1.100",
  "mqtt_port": 1883,
  "mqtt_topic": "flood/topic"
}
```

Copy to `config.json` and fill in actual details.

---

## Troubleshooting

* **Cannot connect to WiFi:** Check SSID/password and ensure Pico W firmware is up to date.
* **No MQTT messages:** Verify broker is running and topics match.
* **Dashboard not showing data:** Check browser console (F12) for JS errors or check backend logs.

---

## Additional Notes

* Keep sensitive info in a separate config file or environment variables.
* Update README if you change file names or code paths in `SourceCode`.

---

## License & Contact

Add a license (e.g., MIT) if you intend to share this project. Contact the repository owner for further help.

---

*This README is a general setup guide for using a Raspberry Pi Pico W with the FloodDetection_IoT project. Adjust filenames and settings according to your actual `SourceCode` folder.*
