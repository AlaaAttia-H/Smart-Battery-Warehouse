# Raspberry Pi Setup

This README explains how to set up and run the Raspberry Pi side of the Smart Battery Warehouse project.

The Raspberry Pi is responsible for:

```text
running Mosquitto MQTT broker
publishing sensor values
reading battery and occupancy input files
receiving actuator commands
controlling fan, buzzer, LED, and shutter
running Node-RED dashboard server
```

## 1. Connect to the Raspberry Pi

From Windows PowerShell:

```powershell
ssh group29@<RASPBERRY_PI_IP>
```

Example:

```powershell
ssh group29@192.168.137.70
```

Check the Raspberry Pi IP:

```bash
hostname -I
```

## 2. Install and Start Mosquitto

Install Mosquitto if it is not already installed:

```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients -y
```

Start Mosquitto:

```bash
sudo systemctl start mosquitto
```

Enable Mosquitto on boot:

```bash
sudo systemctl enable mosquitto
```

Check status:

```bash
sudo systemctl status mosquitto
```

Check that port 1883 is open:

```bash
sudo ss -ltnp | grep 1883
```

## 3. Allow Laptop Connections to Mosquitto

Create or edit:

```bash
sudo nano /etc/mosquitto/conf.d/sciot.conf
```

Add:

```text
listener 1883
allow_anonymous true
```

Restart Mosquitto:

```bash
sudo systemctl restart mosquitto
```

## 4. Create Project Folder on Raspberry Pi

```bash
mkdir -p ~/sciot_project
mkdir -p ~/sciot_project/mqtt
mkdir -p ~/sciot_project/hardware
mkdir -p ~/sciot_project/runtime
```

## 5. Create Virtual Environment

```bash
cd ~/sciot_project
python3 -m venv venv
source venv/bin/activate
```

Install packages:

```bash
pip install paho-mqtt
```

If the hardware code needs GPIO libraries, install the required packages for the specific Raspberry Pi setup.

## 6. Enable pigpio if Used

If the code uses `pigpio` for direct GPIO devices:

```bash
sudo systemctl start pigpiod
sudo systemctl enable pigpiod
sudo systemctl status pigpiod
```

## 7. Copy Raspberry Pi Code from Laptop

From Windows PowerShell, from the project root:

```powershell
scp .\raspberry-pi\src\main.py group29@<RASPBERRY_PI_IP>:/home/group29/sciot_project/main.py
scp .\raspberry-pi\src\battery_input.py group29@<RASPBERRY_PI_IP>:/home/group29/sciot_project/battery_input.py
scp .\raspberry-pi\src\occupancy_input.py group29@<RASPBERRY_PI_IP>:/home/group29/sciot_project/occupancy_input.py
scp .\raspberry-pi\src\mqtt\rpi_hardware_node.py group29@<RASPBERRY_PI_IP>:/home/group29/sciot_project/mqtt/rpi_hardware_node.py
scp .\raspberry-pi\src\mqtt\topics.py group29@<RASPBERRY_PI_IP>:/home/group29/sciot_project/mqtt/topics.py
scp .\raspberry-pi\src\hardware\grove_inputs.py group29@<RASPBERRY_PI_IP>:/home/group29/sciot_project/hardware/grove_inputs.py
scp .\raspberry-pi\src\hardware\grove_outputs.py group29@<RASPBERRY_PI_IP>:/home/group29/sciot_project/hardware/grove_outputs.py
scp .\raspberry-pi\src\hardware\pi_direct.py group29@<RASPBERRY_PI_IP>:/home/group29/sciot_project/hardware/pi_direct.py
```

## 8. Run Raspberry Pi Hardware Node

On the Raspberry Pi:

```bash
cd ~/sciot_project
source venv/bin/activate
python main.py
```

The node publishes:

```text
warehouse/sensors/temperature
warehouse/sensors/humidity
warehouse/sensors/gas_status
warehouse/sensors/occupancy
warehouse/sensors/battery_status
```

The node subscribes to:

```text
warehouse/actuators/fan/command
warehouse/actuators/buzzer/command
warehouse/actuators/led/command
warehouse/actuators/shutter/command
```

## 9. Run Battery Input

Open another Raspberry Pi terminal:

```bash
cd ~/sciot_project
source venv/bin/activate
python battery_input.py
```

Example values:

```text
80 -> normal battery
45 -> low battery
15 -> critical battery
```

## 10. Run Occupancy Input

Open another Raspberry Pi terminal:

```bash
cd ~/sciot_project
source venv/bin/activate
python occupancy_input.py
```

Values:

```text
0 -> no occupancy
1 -> occupancy detected
```

## 11. Troubleshooting

### Laptop cannot connect to broker

Check Pi IP:

```bash
hostname -I
```

Check Mosquitto:

```bash
sudo systemctl status mosquitto
```

Restart Mosquitto:

```bash
sudo systemctl restart mosquitto
```

### I2C/GrovePi error

If this appears:

```text
OSError: [Errno 5] Input/output error
```

Stop scripts and reboot:

```bash
sudo pkill -f main.py
sudo reboot
```

### Check MQTT manually

Subscribe on Pi:

```bash
mosquitto_sub -h localhost -t "warehouse/#" -v
```

Publish test message:

```bash
mosquitto_pub -h localhost -t "warehouse/actuators/led/command" -m "GREEN"
```
