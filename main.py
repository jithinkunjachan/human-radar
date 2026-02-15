import machine
import network
import time
import json
import secrets
from umqtt.simple import MQTTClient


mqtt_address = secrets.mqtt_address
mqtt_user = secrets.mqtt_user
mqtt_password = secrets.mqtt_password
wifi_username = secrets.wifi_username
wifi_password = secrets.wifi_password

discovery = "homeassistant/sensor/jithin/config"
state_topic = "homeassistant/sensor/jithin/state"
detected = "OFF"
distance = 0

payload = {
    "name": "Detected",
    "unique_id": "motion_detected",
    "state_topic": state_topic,
    "value_template": "{{ value_json.detected }}",
    "device": {
        "name": "presence sensor",
        "identifiers": ["jithin"],
        "manufacturer": "rinyjithin",
        "model": "presencesensor",
    },
}

discovery2 = "homeassistant/sensor/jithin2/config"
payload2 = {
    "name": "Distance",
    "unique_id": "distance",
    "state_topic": state_topic,
    "unit_of_measurement": "cm",
    "value_template": "{{ value_json.distance }}",
    "device": {"name": "presence sensor", "identifiers": ["jithin"]},
}


def connect_wifi(ssid, password):
    gc.collect()  # Free memory before wifi init
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)

    wlan.config(txpower=8.5)
    if not wlan.isconnected():
        print("Connecting to network...")
        wlan.connect(ssid, password)

        # Timeout after 10 seconds
        timeout = 20
        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > timeout:
                print("Connection timed out")
                return False
            time.sleep(0.5)

    print("Connected! Network config:", wlan.ifconfig())
    return True


def uart_configure():
    uart = machine.UART(1, baudrate=115200, tx=4, rx=3, timeout=20, parity=None, stop=1)
    # configuration to make presence timeout to 5 seconds
    cmd = b"\xfd\xfc\xfb\xfa\06\x00\x12\x01\x02\x00\x05\x00\x00\x00\x04\x03\x02\x01"
    uart.write(cmd)
    time.sleep(5)
    reply = uart.read(100)
    return uart


def read_radar(uart, client, detected, distance):
    if uart.any():
        data = uart.readline()
        if data:
            try:
                t_distance = distance
                t_detected = detected
                line = data.decode("utf-8").strip()
                if line.startswith("Range"):
                    t_distance = int(line.split(" ")[1])
                elif line == "ON":
                    t_detected = "ON"
                elif line == "OFF":
                    t_detected = "OFF"
            except Exception as e:
                # Handle potential decoding errors from partial frames
                pass
            if t_distance != distance or t_detected != detected:
                detected = t_detected
                distance = t_distance
                print("changed", distance, detected)
                mqtt_publish(
                    client,
                    state_topic,
                    json.dumps({"detected": detected, "distance": distance}),
                    False,
                )

    return detected, distance


def mqtt_reconnect(client):
    while True:
        try:
            print("trying to reconnect")
            client.connect()
        except Exception as e:
            print("exeception when reconnecting")
            time.sleep(20)
            continue
        break


def mqtt_publish(client, topic, jsondumps, retain):
    try:
        client.publish(topic, jsondumps, retain)
    except Exception as e:
        print("exeception when publishing")
        mqtt_reconnect(client)


def mqtt_configure():
    client = MQTTClient(
        "jithin sensor", mqtt_address, user=mqtt_user, password=mqtt_password
    )
    mqtt_reconnect(client)
    time.sleep(5)
    # Publish discovery payloads for Home Assistant
    mqtt_publish(client, discovery, json.dumps(payload), True)
    mqtt_publish(client, discovery2, json.dumps(payload2), True)
    return client


def remove_discovery():
    time.sleep(20)
    mqtt_publish(client, discovery, "", False)
    mqtt_publish(client, discovery2, "", False)
    mqtt_publish(client, state_topic, "", False)


print("WIFI connected successfully...")
# Replace with your credentials
if not connect_wifi(wifi_username, wifi_password):
    print("error while connecting to wifi")

print("configuring the uart")
uart = uart_configure()
print("configuring mqtt")
client = mqtt_configure()
print("reading sensor measurements")

while True:
    t_detected, t_distance = read_radar(uart, client, detected, distance)
    detected = t_detected
    distance = t_distance
