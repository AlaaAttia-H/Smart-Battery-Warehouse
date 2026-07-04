from mqtt.rpi_hardware_node import RaspberryPiHardwareNode


BROKER = "localhost"
PORT = 1883
READ_INTERVAL = 2.0


def main():
    node = RaspberryPiHardwareNode(
        broker=BROKER,
        port=PORT,
        read_interval=READ_INTERVAL,
    )

    node.run()


if __name__ == "__main__":
    main()