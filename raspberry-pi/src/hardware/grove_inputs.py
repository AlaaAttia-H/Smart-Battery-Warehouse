import time
import smbus2
import struct


GROVEPI_ADDRESS = 0x04


def read_dht(bus: smbus2.SMBus, pin: int, dht_type: int):
    """Read DHT sensor via GrovePi+ I2C."""
    bus.i2c_rdwr(smbus2.i2c_msg.write(GROVEPI_ADDRESS, [40, pin, dht_type, 0x0]))
    time.sleep(0.6)

    msg_read = smbus2.i2c_msg.read(GROVEPI_ADDRESS, 9)
    bus.i2c_rdwr(msg_read)

    buf = bytes(msg_read)
    temp = struct.unpack_from("<f", buf, 1)[0]
    hum = struct.unpack_from("<f", buf, 5)[0]

    return temp, hum


# def pin_mode(bus: smbus2.SMBus, pin: int, mode: int):
#     """
#     Set GrovePi pin mode.

#     mode = 0 for input
#     mode = 1 for output
#     """
#     bus.write_i2c_block_data(GROVEPI_ADDRESS, 5, [pin, mode, 0])
#     time.sleep(0.05)


# def read_digital(bus: smbus2.SMBus, pin: int):
#     """
#     Read a digital GrovePi pin.

#     Returns:
#         0 = LOW
#         1 = HIGH
#     """
#     bus.write_i2c_block_data(GROVEPI_ADDRESS, 1, [pin, 0, 0])
#     time.sleep(0.05)

#     value = bus.read_byte(GROVEPI_ADDRESS)
#     return int(value)


# def read_pir(bus: smbus2.SMBus, pin: int):
#     """
#     Read Grove PIR motion sensor.
#     """
#     return read_digital(bus, pin) == 1


# def read_button(bus: smbus2.SMBus, pin: int):
#     """
#     Read Grove button raw digital value.

#     Returns:
#         0 = LOW
#         1 = HIGH
#     """
#     return read_digital(bus, pin)

def _send(bus: smbus2.SMBus, data):
    bus.write_i2c_block_data(GROVEPI_ADDRESS, 0, data)


def _receive(bus: smbus2.SMBus, length):
    return bus.read_i2c_block_data(GROVEPI_ADDRESS, 1, length)


def pin_mode(bus: smbus2.SMBus, pin: int, mode: int):
    """
    Set GrovePi pin mode.

    mode = 0 for input
    mode = 1 for output
    """
    _send(bus, [5, pin, mode, 0])
    time.sleep(0.1)


def read_digital(bus: smbus2.SMBus, pin: int):
    """
    Read a GrovePi digital pin.

    Returns:
        0 = LOW
        1 = HIGH
    """
    _send(bus, [1, pin, 0, 0])
    time.sleep(0.1)

    data = _receive(bus, 4)
    return int(data[1])


def read_button(bus: smbus2.SMBus, pin: int):
    return read_digital(bus, pin)