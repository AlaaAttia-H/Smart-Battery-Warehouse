import os
import time
import pigpio

PWM_PATH = "/sys/class/pwm/pwmchip0"
PWM_CHANNEL = "0"
PWM_PERIOD_NS = 20_000_000


class DCFan:
    """DC fan control via PWM on GPIO18"""

    def __init__(self, period_ns: int = PWM_PERIOD_NS):
        self.period_ns = period_ns
        self._pwm_path = f"{PWM_PATH}/pwm{PWM_CHANNEL}"
        self._running = False
        self._init()

    def _init(self):
        self._unexport_if_exists()
        self._export()
        self._write("period", self.period_ns)
        self._write("duty_cycle", 0)
        self._write("enable", 1)
        self._running = True
        print("[FAN] Initialized")

    def set_speed(self, percent: float):
        """Set fan speed (0-100%)"""
        percent = max(0.0, min(100.0, percent))
        self._write("duty_cycle", self._percent_to_ns(percent))
        print(f"[FAN] Speed {percent:.1f}%")

    def stop(self):
        """Stop fan and release PWM"""
        if self._running:
            self._write("duty_cycle", 0)
            self._write("enable", 0)
            self._unexport_if_exists()
            self._running = False
            print("[FAN] Stopped")

    def _export(self):
        with open(f"{PWM_PATH}/export", "w") as f:
            f.write(PWM_CHANNEL)
        time.sleep(0.1)

    def _unexport_if_exists(self):
        if os.path.exists(self._pwm_path):
            try:
                self._write("enable", 0)
            except OSError:
                pass
            with open(f"{PWM_PATH}/unexport", "w") as f:
                f.write(PWM_CHANNEL)
            time.sleep(0.1)

    def _write(self, attr: str, value):
        with open(f"{self._pwm_path}/{attr}", "w") as f:
            f.write(str(value))

    def _percent_to_ns(self, percent: float) -> int:
        return int(self.period_ns * percent / 100)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stop()


SERVO_MIN_PW = 500
SERVO_MAX_PW = 2500


class Servo:
    """Servo control via pigpio on GPIO22"""

    def __init__(self, gpio_pin: int, min_pw: int = SERVO_MIN_PW, max_pw: int = SERVO_MAX_PW):
        self.pin = gpio_pin
        self.min_pw = min_pw
        self.max_pw = max_pw

        self._pi = pigpio.pi()
        if not self._pi.connected:
            raise RuntimeError("[SERVO] Cannot connect to pigpiod. Start it with: sudo systemctl start pigpiod")
        print("[SERVO] Initialized")

    def set_position(self, angle: float):
        """Set servo position (0-180 degrees)"""
        angle = max(0.0, min(180.0, angle))
        pw = int(self.min_pw + (self.max_pw - self.min_pw) * angle / 180.0)
        self._pi.set_servo_pulsewidth(self.pin, pw)
        print(f"[SERVO] Position {angle:.1f}°")

    def stop(self):
        self._pi.set_servo_pulsewidth(self.pin, 0)
        self._pi.stop()
        print("[SERVO] Stopped")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stop()

class MQ2Sensor:
    """MQ-2 gas sensor (binary output via GPIO27)"""

    def __init__(self, gpio_pin: int):
        self.pin = gpio_pin
        self._pi = pigpio.pi()

        if not self._pi.connected:
            raise RuntimeError("[MQ2] Cannot connect to pigpiod. Start it with: sudo systemctl start pigpiod")

        self._pi.set_mode(self.pin, pigpio.INPUT)
        self._pi.set_pull_up_down(self.pin, pigpio.PUD_UP)
        print("[MQ2] Initialized")

    def is_gas_detected(self) -> bool:
        """Returns True if gas detected (pin LOW)"""
        return self._pi.read(self.pin) == 0

    def stop(self):
        self._pi.stop()
        print("[MQ2] Stopped")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stop()

class RGBLed:
    """RGB LED control via pigpio (common anode)"""

    def __init__(self, pin_r: int, pin_g: int, pin_b: int):
        self.pin_r = pin_r
        self.pin_g = pin_g
        self.pin_b = pin_b

        self._pi = pigpio.pi()
        if not self._pi.connected:
            raise RuntimeError("[RGB] Cannot connect to pigpiod")

        self.set_color(0, 0, 0)
        print("[RGB] Initialized")

    def _set_channel(self, pin: int, value: int):
        if value == 0:
            self._pi.write(pin, 1)
        elif value == 255:
            self._pi.write(pin, 0)
        else:
            self._pi.set_PWM_dutycycle(pin, 255 - value)

    def set_color(self, r: int, g: int, b: int):
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))

        self._set_channel(self.pin_r, r)
        self._set_channel(self.pin_g, g)
        self._set_channel(self.pin_b, b)
        print(f"[LED] Color RGB({r},{g},{b})")

    def stop(self):
        self.set_color(0, 0, 0)
        self._pi.stop()
        print("[LED] Stopped")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stop()
