import time
import smbus2
import struct


def read_dht(bus: smbus2.SMBus, pin: int, dht_type: int):
    """Read DHT sensor via GrovePi+ I2C"""
    addr = 0x04
    bus.i2c_rdwr(smbus2.i2c_msg.write(addr, [40, pin, dht_type, 0x0]))
    time.sleep(0.6)
    msg_read = smbus2.i2c_msg.read(addr, 9)
    bus.i2c_rdwr(msg_read)
    buf = bytes(msg_read)
    temp = struct.unpack_from('<f', buf, 1)[0]
    hum = struct.unpack_from('<f', buf, 5)[0]
    return temp, hum
