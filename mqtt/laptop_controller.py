"""
Laptop MQTT controller.

This file runs on the laptop.
It receives sensor data from the Raspberry Pi and sends actuator commands back.
"""

import time

import paho.mqtt.client as mqtt

try:
    from mqtt.topics import (
        ACTUATOR_BUZZER_COMMAND,
        ACTUATOR_FAN_COMMAND,
        ACTUATOR_LED_COMMAND,
        ACTUATOR_SHUTTER_COMMAND,
        CONTEXT_RISK_LEVEL,
        NOTIFICATION_MANAGER,
        PLANNING_PLAN,
        SENSOR_CO2,
        SENSOR_GAS_ALERT,
        SENSOR_TEMPERATURE,
    )
except ImportError:
    from topics import (
        ACTUATOR_BUZZER_COMMAND,
        ACTUATOR_FAN_COMMAND,
        ACTUATOR_LED_COMMAND,
        ACTUATOR_SHUTTER_COMMAND,
        CONTEXT_RISK_LEVEL,
        NOTIFICATION_MANAGER,
        PLANNING_PLAN,
        SENSOR_CO2,
        SENSOR_GAS_ALERT,
        SENSOR_TEMPERATURE,
    )


BROKER = "10.63.50.207"   # Raspberry Pi IP address
PORT = 1883


class LaptopController:
    def __init__(self):
        self.broker = BROKER
        self.port = PORT

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.sensor_state = {}
        self.last_published = {}

    def connect(self):
        print(f"[MQTT] Connecting to broker at {self.broker}:{self.port}")
        self.client.connect(self.broker, self.port, keepalive=60)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"[MQTT] Connected: {reason_code}")

        client.subscribe("warehouse/sensors/#")
        print("[MQTT] Subscribed to warehouse/sensors/#")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        message = msg.payload.decode(errors="replace").strip()

        print(f"[SENSOR RECEIVED] {topic} -> {message}")

        self.sensor_state[topic] = message
        self.evaluate_system_state()

    def get_float(self, topic, default=None):
        try:
            return float(self.sensor_state.get(topic, default))
        except (TypeError, ValueError):
            return default

    def get_bool(self, topic):
        value = str(self.sensor_state.get(topic, "")).lower()
        return value in ["1", "true", "yes", "on", "alert", "high"]

    def evaluate_system_state(self):
        temperature = self.get_float(SENSOR_TEMPERATURE)
        co2 = self.get_float(SENSOR_CO2)
        gas_alert = self.get_bool(SENSOR_GAS_ALERT)

        if temperature is None:
            return

        risk_level = self.calculate_risk_level(
            temperature=temperature,
            co2=co2,
            gas_alert=gas_alert,
        )

        commands, plan = self.decide_actions(risk_level)

        self.publish_if_changed(CONTEXT_RISK_LEVEL, risk_level)
        self.publish_if_changed(PLANNING_PLAN, plan)

        for topic, command in commands.items():
            self.publish_if_changed(topic, command)

        if risk_level == "HIGH":
            self.publish_if_changed(
                NOTIFICATION_MANAGER,
                "High warehouse risk detected. Emergency actions activated.",
            )

    def calculate_risk_level(self, temperature, co2, gas_alert):
        if gas_alert:
            return "HIGH"

        if temperature >= 40:
            return "HIGH"

        if co2 is not None and co2 >= 1000:
            return "HIGH"

        if temperature >= 32:
            return "MEDIUM"

        if co2 is not None and co2 >= 800:
            return "MEDIUM"

        return "LOW"

    def decide_actions(self, risk_level):
        if risk_level == "HIGH":
            commands = {
                ACTUATOR_FAN_COMMAND: "ON",
                ACTUATOR_BUZZER_COMMAND: "ON",
                ACTUATOR_LED_COMMAND: "RED",
                ACTUATOR_SHUTTER_COMMAND: "CLOSE",
            }

            plan = (
                "start-fan; "
                "activate-alarm; "
                "turn-on-warning-light; "
                "close-shutter; "
                "notify-manager"
            )

        elif risk_level == "MEDIUM":
            commands = {
                ACTUATOR_FAN_COMMAND: "ON",
                ACTUATOR_BUZZER_COMMAND: "OFF",
                ACTUATOR_LED_COMMAND: "ORANGE",
                ACTUATOR_SHUTTER_COMMAND: "OPEN",
            }

            plan = (
                "start-fan; "
                "turn-on-warning-light; "
                "open-shutter"
            )

        else:
            commands = {
                ACTUATOR_FAN_COMMAND: "OFF",
                ACTUATOR_BUZZER_COMMAND: "OFF",
                ACTUATOR_LED_COMMAND: "GREEN",
                ACTUATOR_SHUTTER_COMMAND: "OPEN",
            }

            plan = (
                "stop-fan; "
                "stop-alarm; "
                "set-safe-light; "
                "open-shutter"
            )

        return commands, plan

    def publish_if_changed(self, topic, message):
        if self.last_published.get(topic) == message:
            return

        self.client.publish(topic, message)
        self.last_published[topic] = message

        print(f"[COMMAND SENT] {topic} -> {message}")

    def run(self):
        self.connect()

        print("[SYSTEM] Laptop controller running")
        print("[SYSTEM] Press Ctrl+C to stop")

        try:
            self.client.loop_forever()

        except KeyboardInterrupt:
            print("\n[SYSTEM] Stopping laptop controller...")

        finally:
            self.client.disconnect()
            time.sleep(0.5)
            print("[SYSTEM] Laptop controller stopped")


def main():
    controller = LaptopController()
    controller.run()


if __name__ == "__main__":
    main()