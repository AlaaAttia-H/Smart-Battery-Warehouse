"""
Raspberry Pi MQTT hardware node.

"""

import random
import time

import paho.mqtt.client as mqtt
import smbus2

from hardware.grove_inputs import read_dht
from hardware.grove_outputs import GroveBuzzer
from hardware.pi_direct import DCFan, MQ2Sensor, RGBLed, Servo

from mqtt.topics import (
    ACTUATOR_BUZZER_COMMAND,
    ACTUATOR_COMMAND_TOPICS,
    ACTUATOR_FAN_COMMAND,
    ACTUATOR_LED_COMMAND,
    ACTUATOR_SHUTTER_COMMAND,
    CONTEXT_RISK_LEVEL,
    SENSOR_BATTERY_STATUS,
    SENSOR_CO2,
    SENSOR_GAS_ALERT,
    SENSOR_HUMIDITY,
    SENSOR_OCCUPANCY,
    SENSOR_TEMPERATURE,
)


# GrovePi / sensor configuration
DHT_PIN = 4
DHT_TYPE = 0

# Direct Raspberry Pi GPIO configuration
SERVO_PIN = 22
MQ2_PIN = 27

LED_R_PIN = 25
LED_G_PIN = 24
LED_B_PIN = 23

BUZZER_PIN = 3

SIMULATE_MISSING_SENSORS = True


class RaspberryPiHardwareNode:
    def __init__(self, broker="localhost", port=1883, read_interval=2.0):
        self.broker = broker
        self.port = port
        self.read_interval = read_interval

        self.bus = None
        self.client = None

        self.fan = None
        self.servo = None
        self.mq2 = None
        self.led = None
        self.buzzer = None

        self.simulated_battery = 100
        self.simulated_occupancy = 0

    def open_bus(self):
        bus = smbus2.SMBus(1)
        time.sleep(1)
        return bus

    def setup_hardware(self):
        print("[SYSTEM] Initialising hardware...")

        self.bus = self.open_bus()

        self.fan = DCFan()
        self.servo = Servo(gpio_pin=SERVO_PIN)
        self.mq2 = MQ2Sensor(gpio_pin=MQ2_PIN)
        self.led = RGBLed(pin_r=LED_R_PIN, pin_g=LED_G_PIN, pin_b=LED_B_PIN)

        self.buzzer = GroveBuzzer(pin=BUZZER_PIN)
        self.buzzer.update_bus(self.bus)

        # Safe initial state
        self.fan.set_speed(0)
        self.servo.set_position(90)
        self.led.set_color(0, 0, 0)
        self.buzzer.stop_siren()

        print("[SYSTEM] Hardware ready")

    def setup_mqtt(self):
        print(f"[MQTT] Connecting to broker at {self.broker}:{self.port}")

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.broker, self.port, keepalive=60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"[MQTT] Connected: {reason_code}")

        for topic in ACTUATOR_COMMAND_TOPICS:
            client.subscribe(topic)
            print(f"[MQTT] Subscribed to {topic}")

        # Optional backup: the Pi can also react directly to risk level.
        client.subscribe(CONTEXT_RISK_LEVEL)
        print(f"[MQTT] Subscribed to {CONTEXT_RISK_LEVEL}")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        message = msg.payload.decode(errors="replace").strip()

        print(f"[MQTT RECEIVED] {topic} -> {message}")

        try:
            if topic == ACTUATOR_FAN_COMMAND:
                self.handle_fan_command(message)

            elif topic == ACTUATOR_BUZZER_COMMAND:
                self.handle_buzzer_command(message)

            elif topic == ACTUATOR_LED_COMMAND:
                self.handle_led_command(message)

            elif topic == ACTUATOR_SHUTTER_COMMAND:
                self.handle_shutter_command(message)


        except Exception as e:
            print(f"[MQTT ERROR] Could not handle command: {e}")

    def handle_fan_command(self, command):
        command = command.upper()

        if command in ["ON", "START", "1", "TRUE"]:
            self.fan.set_speed(100)

        elif command in ["OFF", "STOP", "0", "FALSE"]:
            self.fan.set_speed(0)

        else:
            # Allow numeric speed, for example: "50"
            speed = float(command)
            self.fan.set_speed(speed)

    def handle_buzzer_command(self, command):
        command = command.upper()

        if command in ["ON", "START", "SIREN", "ALARM", "1", "TRUE"]:
            self.buzzer.start_siren()

        elif command in ["OFF", "STOP", "0", "FALSE"]:
            self.buzzer.stop_siren()

    def handle_led_command(self, command):
        command = command.upper()

        colors = {
            "OFF": (0, 0, 0),
            "RED": (255, 0, 0),
            "ORANGE": (255, 70, 0),
            "GREEN": (0, 255, 0),
            "BLUE": (0, 0, 255),
            "WHITE": (255, 255, 255),
        }

        if command in colors:
            r, g, b = colors[command]
            self.led.set_color(r, g, b)
            return

        parts = command.split(",")
        if len(parts) == 3:
            r, g, b = [int(part.strip()) for part in parts]
            self.led.set_color(r, g, b)

    def handle_shutter_command(self, command):
        command = command.upper()

        if command in ["OPEN", "UP"]:
            self.servo.set_position(90)

        elif command in ["CLOSE", "CLOSED", "DOWN"]:
            self.servo.set_position(0)

        elif command in ["HALF", "MIDDLE"]:
            self.servo.set_position(45)

        else:
            angle = float(command)
            self.servo.set_position(angle)

    def handle_risk_level(self, risk_level):
        risk_level = risk_level.upper()

        # This is only a backup reaction.
        # The laptop controller also sends direct actuator commands.
        if risk_level == "HIGH":
            self.fan.set_speed(100)
            self.buzzer.start_siren()
            self.led.set_color(255, 0, 0)
            self.servo.set_position(0)

        elif risk_level == "MEDIUM":
            self.fan.set_speed(100)
            self.buzzer.stop_siren()
            self.led.set_color(255, 70, 0)
            self.servo.set_position(90)

        elif risk_level == "LOW":
            self.fan.set_speed(0)
            self.buzzer.stop_siren()
            self.led.set_color(0, 255, 0)
            self.servo.set_position(90)

    def publish(self, topic, value):
        self.client.publish(topic, str(value))

    def publish_sensor_data(self):
        try:
            temperature, humidity = read_dht(self.bus, DHT_PIN, DHT_TYPE)
            gas_alert = self.mq2.is_gas_detected()

            co2_proxy = 1500 if gas_alert else 400

            self.publish(SENSOR_TEMPERATURE, round(temperature, 1))
            self.publish(SENSOR_HUMIDITY, round(humidity, 1))
            self.publish(SENSOR_GAS_ALERT, int(gas_alert))
            self.publish(SENSOR_CO2, co2_proxy)

            if SIMULATE_MISSING_SENSORS:
                self.simulated_battery = max(
                    0,
                    self.simulated_battery - random.choice([0, 0, 0, 1]),
                )
                self.simulated_occupancy = random.randint(0, 10)

                self.publish(SENSOR_BATTERY_STATUS, self.simulated_battery)
                self.publish(SENSOR_OCCUPANCY, self.simulated_occupancy)

            print(
                f"[SENSORS] T={temperature:.1f}C "
                f"H={humidity:.1f}% "
                f"GAS={'ALERT' if gas_alert else 'OK'}"
            )

        except OSError as e:
            print(f"[I2C ERROR] {e}")
            self.reopen_bus()

        except Exception as e:
            print(f"[SENSOR ERROR] {e}")

    def reopen_bus(self):
        try:
            if self.bus:
                self.bus.close()
        except Exception:
            pass

        time.sleep(2)
        self.bus = self.open_bus()

        if self.buzzer:
            self.buzzer.update_bus(self.bus)

    def run(self):
        try:
            self.setup_hardware()
            self.setup_mqtt()

            print("[SYSTEM] Raspberry Pi MQTT hardware node running")

            while True:
                self.publish_sensor_data()
                time.sleep(self.read_interval)

        except KeyboardInterrupt:
            print("\n[SYSTEM] Stopping...")

        finally:
            self.cleanup()

    def cleanup(self):
        print("[SYSTEM] Cleaning up...")

        try:
            if self.fan:
                self.fan.set_speed(0)
                self.fan.stop()

            if self.servo:
                self.servo.stop()

            if self.mq2:
                self.mq2.stop()

            if self.led:
                self.led.stop()

            if self.buzzer:
                self.buzzer.stop_siren()

            if self.bus:
                self.bus.close()

            if self.client:
                self.client.loop_stop()
                self.client.disconnect()

        except Exception as e:
            print(f"[CLEANUP ERROR] {e}")

        print("[SYSTEM] Stopped")