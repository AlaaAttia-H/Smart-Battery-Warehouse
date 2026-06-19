"""
Test MQTT Subscriber.
"""

import paho.mqtt.client as mqtt

BROKER = "localhost"   # change to Raspberry Pi IP or laptop IP
PORT = 1883

def on_message(client, userdata, msg):
    topic = msg.topic
    message = msg.payload.decode()

    print(f"[RECEIVED] {topic} → {message}")

    # actuator logic simulation
    if topic == "warehouse/actuators/fan/command":
        if message == "ON":
            print("FAN TURNED ON")
        else:
            print("FAN TURNED OFF")

    if topic == "warehouse/context/risk_level":
        print(f"RISK LEVEL: {message}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.on_message = on_message
client.connect(BROKER, PORT)

# subscribe to ALL warehouse messages
client.subscribe("warehouse/#")

print("Subscriber running... waiting for messages")
client.loop_forever()