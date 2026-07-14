"""
Raspberry Pi MQTT hardware node.
"""

import json
import time
from pathlib import Path

import paho.mqtt.client as mqtt

from hardware.grove_inputs import pin_mode, read_button, read_dht
from hardware.grove_outputs import GroveBuzzer
from hardware.pi_direct import DCFan, MQ2Sensor, RGBLed, Servo

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


# GrovePi configuration
DHT_PIN = 4
DHT_TYPE = 0

BUZZER_PIN = 3

BUTTON_PIN = 8
BUTTON_DEBOUNCE_SECONDS = 0.3
BUTTON_ACTIVE_LOW = False

# Direct Raspberry Pi GPIO configuration
SERVO_PIN = 22
SERVO_OPEN_ANGLE = 90
SERVO_CLOSE_ANGLE = 20
SERVO_HALF_ANGLE = 45

SERVO_STEP = 2
SERVO_STEP_DELAY = 0.03
MQ2_PIN = 27

LED_R_PIN = 25
LED_G_PIN = 24
LED_B_PIN = 23

# Battery input file
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
        self.current_servo_angle = SERVO_OPEN_ANGLE
        self.mq2 = None
        self.led = None
        self.buzzer = None

        self.occupancy = 0
        self.last_button_state = None
        self.last_button_toggle_time = 0

    def open_bus(self):
        import smbus2

        bus = smbus2.SMBus(1)
        time.sleep(1)
        return bus

    def setup_button(self):
        try:
            pin_mode(self.bus, BUTTON_PIN, 0)
            print(f"[BUTTON] Initialised on Grove D{BUTTON_PIN}")

        except OSError as e:
            print(f"[BUTTON WARNING] Button setup failed: {e}")
            print("[BUTTON WARNING] Continuing. Button reads may fail until I2C recovers.")

    def setup_hardware(self):
        print("[SYSTEM] Initialising hardware...")

        self.bus = self.open_bus()

        self.setup_button()

        self.fan = DCFan()
        self.servo = Servo(gpio_pin=SERVO_PIN)
        self.mq2 = MQ2Sensor(gpio_pin=MQ2_PIN)
        self.led = RGBLed(pin_r=LED_R_PIN, pin_g=LED_G_PIN, pin_b=LED_B_PIN)

        self.buzzer = GroveBuzzer(pin=BUZZER_PIN)
        self.buzzer.update_bus(self.bus)

        self.fan.set_speed(0)
        self.move_servo_slowly(SERVO_OPEN_ANGLE)
        self.led.set_color(0, 0, 0)
        self.buzzer.stop_siren()

        print("[SYSTEM] Hardware ready")

    def reopen_bus(self):
        print("[I2C] Reopening I2C bus...")

        try:
            if self.bus:
                self.bus.close()
        except Exception as e:
            print(f"[I2C WARNING] Could not close bus: {e}")

        time.sleep(2)

        self.bus = self.open_bus()
        time.sleep(1)

        try:
            pin_mode(self.bus, BUTTON_PIN, 0)
            print("[I2C] Button reconfigured")
        except OSError as e:
            print(f"[BUTTON WARNING] Could not reconfigure button: {e}")

        if self.buzzer:
            self.buzzer.update_bus(self.bus)

        print("[I2C] Bus reopened")

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

    def publish(self, topic, value):
        if self.client:
            self.client.publish(topic, str(value))

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
            self.buzzer.turn_on()

        elif command in ["OFF", "STOP", "0", "FALSE"]:
            self.buzzer.turn_off()

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

    def move_servo_slowly(self, target_angle):
        target_angle = max(0, min(180, int(target_angle)))
        current_angle = int(self.current_servo_angle)

        if current_angle == target_angle:
            return

        if target_angle > current_angle:
            step = SERVO_STEP
        else:
            step = -SERVO_STEP

        for angle in range(current_angle, target_angle, step):
            self.servo.set_position(angle)
            time.sleep(SERVO_STEP_DELAY)

        self.servo.set_position(target_angle)
        self.current_servo_angle = target_angle

    def handle_shutter_command(self, command):
        command = command.upper()

        if command in ["OPEN", "UP"]:
            self.move_servo_slowly(SERVO_OPEN_ANGLE)

        elif command in ["CLOSE", "CLOSED", "DOWN"]:
            self.move_servo_slowly(SERVO_CLOSE_ANGLE)

        elif command in ["HALF", "MIDDLE"]:
            self.move_servo_slowly(SERVO_HALF_ANGLE)

        else:
            angle = float(command)
            self.move_servo_slowly(angle)

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
                    print(f"[BUTTON] Occupancy toggled to {self.occupancy}")

            self.last_button_state = current_button_state
            return self.occupancy

        except OSError as e:
            print(f"[BUTTON I2C ERROR] {e}")
            return self.occupancy

        except Exception as e:
            print(f"[BUTTON ERROR] {e}")
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

            try:
                self.reopen_bus()
            except Exception as reopen_error:
                print(f"[I2C ERROR] Recovery failed: {reopen_error}")

        except Exception as e:
            print(f"[SENSOR ERROR] {e}")

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
            if self.client:
                self.client.loop_stop()
                self.client.disconnect()

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

        except Exception as e:
            print(f"[CLEANUP ERROR] {e}")

        print("[SYSTEM] Stopped")