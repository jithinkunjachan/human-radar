# Human Radar - Presence Sensor

A MicroPython-based human presence detection system using a radar sensor connected to a Raspberry Pi Pico. The sensor detects presence and measures distance, publishing data to Home Assistant via MQTT for home automation integration.

## Features

- **Presence Detection**: Real-time detection of human presence (ON/OFF)
- **Distance Measurement**: Measures distance to detected objects in centimeters
- **MQTT Integration**: Publishes sensor data to MQTT broker for Home Assistant integration
- **Home Assistant Discovery**: Automatic device discovery in Home Assistant
- **WiFi Connectivity**: Connects to WiFi networks for remote data transmission
- **Configurable Timeout**: Adjustable presence detection timeout (default 5 seconds)

## Hardware Requirements

- Raspberry Pi Pico (RP2040)
- Human presence radar sensor module (connected via UART)
- WiFi module or built-in connectivity
- Micro USB cable for power and programming

## Installation

### 1. Flash MicroPython to Raspberry Pi Pico

Download the latest MicroPython firmware for Pico from [micropython.org](https://micropython.org/download/rp2-pico/) and flash it following the official instructions.

### 2. Upload Project Files

Copy the following files to your Pico:

```
/boot.py
/main.py
/secrets.py
/lib/
    /ssl.py
    /umqtt/
        /simple.py
```

### 3. Configure Credentials

Edit `secrets.py` with your WiFi and MQTT credentials:

```python
mqtt_address = "192.168.1.100"  # Your MQTT broker address
mqtt_user = "username"
mqtt_password = "password"
wifi_username = "SSID"
wifi_password = "WiFi_password"
```

## Wiring

Connect the radar sensor to the Pico via UART:
- **TX (Radar)** → GPIO 4 (Pico UART1 TX)
- **RX (Radar)** → GPIO 3 (Pico UART1 RX)
- **GND** → GND
- **VCC** → 3.3V or 5V (depending on sensor)

## Usage

1. Power on the Raspberry Pi Pico
2. The device will connect to WiFi and MQTT broker
3. Sensor data is published to `homeassistant/sensor/jithin/state` as JSON:
   ```json
   {
       "detected": "ON",
       "distance": 150
   }
   ```

## Home Assistant Integration

The device supports Home Assistant MQTT Discovery. Two sensors are automatically created:

- **Detected**: Binary presence state (ON/OFF)
- **Distance**: Distance measurement in centimeters

Both sensors appear under the device named "presence sensor" with ID "jithin".

## MQTT Topics

- **Discovery (Detected)**: `homeassistant/sensor/jithin/config`
- **Discovery (Distance)**: `homeassistant/sensor/jithin2/config`
- **State**: `homeassistant/sensor/jithin/state`

## Configuration Details

### Radar Sensor Setup
The UART is configured with:
- Baud rate: 115200
- TX Pin: GPIO 4
- RX Pin: GPIO 3
- Presence timeout: 5 seconds (configurable via UART command)

### MQTT Connection
- Uses TLS/SSL for secure connections
- Automatic reconnection with 20-second retry interval
- Retain flag enabled for discovery payloads

## Troubleshooting

### WiFi Connection Issues
- Verify SSID and password in `secrets.py`
- Check signal strength (txpower is set to 8.5)
- Ensure sufficient memory (garbage collection is called before WiFi init)

### MQTT Connection Issues
- Verify broker address is correct
- Check username and password credentials
- Ensure MQTT broker is accessible on the network

### Sensor Not Detecting
- Check UART wiring connections
- Verify radar sensor is powered correctly
- Monitor serial output for UART data

## Dependencies

- `umqtt.simple`: MQTT client library
- `ssl`: SSL/TLS support for secure connections
- Standard MicroPython libraries: `machine`, `network`, `time`, `json`

## Debugging

Connect to the Pico via USB serial monitor (115200 baud) to see debug output:
- WiFi connection status
- MQTT connection attempts
- Sensor state changes
- UART data reception

## License

[Specify your license here]

## Author

Based on work by jithinkunjachan
