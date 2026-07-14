import smbus2
import time
import threading


class GroveBuzzer:
    """Grove buzzer control via GrovePi+ I2C"""

    def __init__(self, pin: int):
        self.pin = pin
        self.addr = 0x04
        self._bus = None
        self._siren_running = False
        self._thread = None

    def update_bus(self, bus: smbus2.SMBus):
        self._bus = bus
        try:
            self._bus.i2c_rdwr(smbus2.i2c_msg.write(self.addr, [5, self.pin, 1, 0]))
        except:
            pass

    def _write(self, value: int):
        if self._bus:
            try:
                self._bus.i2c_rdwr(smbus2.i2c_msg.write(self.addr, [2, self.pin, value, 0]))
            except:
                pass

    def start_siren(self):
        if not self._siren_running:
            self._siren_running = True
            self._thread = threading.Thread(target=self._siren_loop, daemon=True)
            self._thread.start()
            print(f"[BUZZER] Siren started")

    def stop_siren(self):
        if self._siren_running:
            self._siren_running = False
            if self._thread:
                self._thread.join(timeout=1.0)
                self._thread = None
            self._write(0)

    def _siren_loop(self):
        while self._siren_running:
            self._write(1)
            time.sleep(0.1)
            if not self._siren_running:
                break
            self._write(0)
            time.sleep(0.4)

    def turn_on(self):
        self._siren_running = False

        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

        for _ in range(2):
            self._write(1)
            time.sleep(0.08)
            self._write(0)
            time.sleep(0.25)

        print("[BUZZER] Two beeps")


    def turn_off(self):
        self._siren_running = False

        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

        self._write(0)
        print("[BUZZER] OFF")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stop_siren()
