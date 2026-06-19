import smbus2
import time

from hardware.pi_direct import DCFan, Servo, MQ2Sensor, RGBLed
from hardware.grove_outputs import GroveBuzzer
from hardware.grove_inputs import read_dht

# Configuration
DHT_PIN = 4
DHT_TYPE = 0
READ_INTERVAL = 2.0

FAN_PIN = 18
SERVO_PIN = 22
MQ2_PIN = 27

LED_R_PIN = 25
LED_G_PIN = 24
LED_B_PIN = 23

BUZZER_PIN = 3

COLORS = [("RED", 255, 0, 0), ("ORANGE", 255, 70, 0), ("GREEN", 0, 255, 0), ("BLUE", 0, 0, 255)]


def open_bus() -> smbus2.SMBus:
    bus = smbus2.SMBus(1)
    time.sleep(1)
    return bus


def main():
    bus = open_bus()
    fan = DCFan()
    servo = Servo(gpio_pin=SERVO_PIN)
    mq2 = MQ2Sensor(gpio_pin=MQ2_PIN)
    led = RGBLed(pin_r=LED_R_PIN, pin_g=LED_G_PIN, pin_b=LED_B_PIN)
    buzzer = GroveBuzzer(pin=BUZZER_PIN)
    buzzer.update_bus(bus)

    color_index = 0
    fan.set_speed(0)
    servo.set_position(90)
    led.set_color(0, 0, 0)
    buzzer.stop_siren()

    print("[SYSTEM] Starting...")

    try:
        while True:
            try:
                # Testing all sensors and actuators in a loop

                temp, hum = read_dht(bus, DHT_PIN, DHT_TYPE)
                gas_alert = mq2.is_gas_detected()

                print(f"[DHT] T={temp:.1f}C  H={hum:.1f}%")
                print(f"[GAS] {'ALERT' if gas_alert else 'OK'}")

                r, g, b = COLORS[color_index][1:]
                led.set_color(r, g, b)
                print(f"[LED] {COLORS[color_index][0]}")
                color_index = (color_index + 1) % len(COLORS)

                fan.set_speed(100)
                servo.set_position(45)

                # Decomment to test buzzer siren
                # buzzer.start_siren()

            except OSError as e:
                print(f"[I2C ERROR] {e}")
                led.set_color(0, 0, 255)
                buzzer.stop_siren()
                try:
                    bus.close()
                except:
                    pass
                time.sleep(2)
                bus = open_bus()
                buzzer.update_bus(bus)

            time.sleep(READ_INTERVAL)

    except KeyboardInterrupt:
        print("\n[SYSTEM] Stopping...")

    finally:
        fan.set_speed(0)
        fan.stop()
        servo.stop()
        mq2.stop()
        led.stop()
        buzzer.stop_siren()
        try:
            bus.close()
        except:
            pass
        print("[SYSTEM] Stopped")

if __name__ == "__main__":
    main()
