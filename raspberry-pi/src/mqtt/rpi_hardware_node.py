"""
Raspberry Pi MQTT hardware node.
"""

import random
import time

import paho.mqtt.client as mqtt
import smbus2

from hardware.grove_inputs import pin_mode, read_dht, read_button
from hardware.grove_outputs import GroveBuzzer
from hardware.pi_direct import DCFan, MQ2Sensor, RGBLed, Servo
import json
from pathlib import Path

from mqtt.topics import (
    ACTUATOR_BUZZER_COMMAND,
    ACTUATOR_COMMAND_TOPICS,
    ACTUATOR_FAN_COMMAND,
    ACTUATOR_LED_COMMAND,
    ACTUATOR_SHUTTER_COMMAND,
    SENSOR_BATTERY_STATUS,
    SENSOR_GAS_STATUS,
    SENSOR_HUMIDITY,
    SENSOR_OCCUPANCY,
    SENSOR_TEMPERATURE,
)


# GrovePi / sensor configuration
DHT_PIN = 4
DHT_TYPE = 0

BUZZER_PIN = 3

BUTTON_PIN = 8
BUTTON_DEBOUNCE_SECONDS = 0.3
BUTTON_ACTIVE_LOW = False

# Direct Raspberry Pi GPIO configuration
SERVO_PIN = 22
MQ2_PIN = 27

LED_R_PIN = 25
LED_G_PIN = 24
LED_B_PIN = 23

# Battery is still simulated because we do not have a real battery sensor.
SIMULATE_BATTERY = False
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BATTERY_STATE_FILE = PROJECT_ROOT / "runtime" / "battery_state.json"
DEFAULT_BATTERY_STATUS = 100


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

        # Used for button-based occupancy
        self.occupancy = 0
        self.last_button_state = None
        self.last_button_toggle_time = 0

    def open_bus(self):
        bus = smbus2.SMBus(1)
        time.sleep(1)
        return bus

    def setup_hardware(self):
        print("[SYSTEM] Initialising hardware...")

        self.bus = self.open_bus()

        pin_mode(self.bus, BUTTON_PIN, 0)

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
            self.fan.set_speed(70)

        elif command in ["OFF", "STOP", "0", "FALSE"]:
            self.fan.set_speed(0)

        else:
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

        # Also allow RGB format, for example: 255,0,0
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

    def read_battery_status(self):
        try:
            if not BATTERY_STATE_FILE.exists():
                return DEFAULT_BATTERY_STATUS

            with open(BATTERY_STATE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            battery_status = int(data.get("battery_status", DEFAULT_BATTERY_STATUS))

            if battery_status < 0:
                return 0

            if battery_status > 100:
                return 100

            return battery_status

        except Exception as e:
            print(f"[BATTERY ERROR] Could not read battery state: {e}")
            return DEFAULT_BATTERY_STATUS

    def publish(self, topic, value):
        self.client.publish(topic, str(value))

    def read_occupancy_from_button(self):
        try:
            raw_value = read_button(self.bus, BUTTON_PIN)

            if BUTTON_ACTIVE_LOW:
                button_pressed = raw_value == 0
            else:
                button_pressed = raw_value == 1

            current_button_state = 1 if button_pressed else 0
            now = time.time()

            if self.last_button_state is None:
                self.last_button_state = current_button_state
                return self.occupancy

            if current_button_state == 1 and self.last_button_state == 0:
                if now - self.last_button_toggle_time > BUTTON_DEBOUNCE_SECONDS:
                    self.occupancy = 0 if self.occupancy == 1 else 1
                    self.last_button_toggle_time = now

            self.last_button_state = current_button_state
            return self.occupancy

        except OSError as e:
            print(f"[BUTTON I2C ERROR] {e}")
            return self.occupancy
    def publish_sensor_data(self):
        try:
            temperature, humidity = read_dht(self.bus, DHT_PIN, DHT_TYPE)

            gas_alert = self.mq2.is_gas_detected()
            gas_status = "ALERT" if gas_alert else "OK"

            occupancy = self.read_occupancy_from_button()
            battery_status = self.read_battery_status()

            self.publish(SENSOR_TEMPERATURE, round(temperature, 1))
            self.publish(SENSOR_HUMIDITY, round(humidity, 1))
            self.publish(SENSOR_GAS_STATUS, gas_status)
            self.publish(SENSOR_OCCUPANCY, occupancy)
            self.publish(SENSOR_BATTERY_STATUS, battery_status)


            print(
                f"[SENSORS] T={temperature:.1f}C "
                f"H={humidity:.1f}% "
                f"GAS={gas_status} "
                f"OCCUPANCY={occupancy} "
                f"BATTERY={battery_status}%"
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

        # Reconfigure Grove digital ports after reopening the I2C bus
        pin_mode(self.bus, BUTTON_PIN, 0)

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