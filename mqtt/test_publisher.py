"""
Test MQTT Publisher.
"""

import paho.mqtt.client as mqtt
import time
import random

BROKER = "localhost"   # change to Raspberry Pi / broker IP
PORT = 1883

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT)


def publish_sensor_data():
    temperature = random.randint(25, 50)
    humidity = random.randint(30, 70)
    co2 = random.randint(400, 1500)
    battery = random.randint(20, 100)
    occupancy = random.randint(0, 10)

    client.publish("warehouse/sensors/temperature", temperature)
    client.publish("warehouse/sensors/humidity", humidity)
    client.publish("warehouse/sensors/co2", co2)
    client.publish("warehouse/sensors/battery_status", battery)
    client.publish("warehouse/sensors/occupancy", occupancy)

    print("Sensors sent")


while True:
    publish_sensor_data()
    time.sleep(3)