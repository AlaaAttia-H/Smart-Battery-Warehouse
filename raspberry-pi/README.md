# Raspberry Pi Setup and Run Guide

This README explains the Raspberry Pi side of the Smart Battery Warehouse project.

The Raspberry Pi is responsible for:

```text
running the Mosquitto MQTT broker
running the Raspberry Pi hardware node
publishing sensor values
reading the Grove button for occupancy
reading battery status from a JSON input file
receiving actuator commands
controlling the fan, buzzer, RGB LED, and shutter/servo
running the Node-RED dashboard server
```

## 1. Hardware and Pi Information

```text
Model: Raspberry Pi Model B+
OS: Raspberry Pi OS Lite 32-bit
Hostname: SCIOT
Username: group29
Password: SCIOT29-group
```


## 2. Project Structure on the Raspberry Pi

The code should be copied to:

```text
/home/group29/sciot_project/
```

Expected structure:

```text
sciot_project/
├── main.py
├── battery_simulator.py
├── runtime/
│   └── battery_state.json
├── hardware/
│   ├── grove_inputs.py
│   ├── grove_outputs.py
│   └── pi_direct.py
└── mqtt/
    ├── rpi_hardware_node.py
    └── topics.py
```

## 3. Connect to the Raspberry Pi

From Windows PowerShell:

```powershell
ssh group29@SCIOT.local
```

or:

```powershell
ssh group29@<RASPBERRY_PI_IP>
```

To check the Raspberry Pi IP after logging in:

```bash
hostname -I
```

## 4. Install and Start Mosquitto

Mosquitto is the MQTT broker. It runs on the Raspberry Pi.

Check if Mosquitto is running:

sudo systemctl status mosquitto


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

Check that port `1883` is open:

```bash
sudo ss -ltnp | grep 1883
```
Install Mosquitto if needed:

```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients -y
```

## 5. Allow Laptop Connections to Mosquitto

If the laptop controller cannot connect to the broker, create or edit:

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

## 6. Create Project Folder on Raspberry Pi

```bash
mkdir -p ~/sciot_project
mkdir -p ~/sciot_project/mqtt
mkdir -p ~/sciot_project/hardware
mkdir -p ~/sciot_project/runtime
```

## 7. Create and Activate Virtual Environment

```bash
cd ~/sciot_project
python3 -m venv venv
source venv/bin/activate
```

Install required Python packages:

```bash
pip install paho-mqtt
```

If needed, also install the hardware libraries used by the Pi code:

```bash
pip install smbus2 pigpio
```

## 8. Enable pigpio

The servo, MQ2 sensor, and RGB LED use direct Raspberry Pi GPIO through `pigpio`.

Check status:

```bash
sudo systemctl status pigpiod
```


Start pigpio:

```bash
sudo systemctl start pigpiod
```

Enable on boot:

```bash
sudo systemctl enable pigpiod
```


## 9. Copy Raspberry Pi Code from Laptop to Pi

From Windows PowerShell, run these commands from the main project root:

```powershell
scp -r .\raspberry-pi\src\ group29@<RASPBERRY_PI_IP>:/home/group29/sciot_project/
```

Example:

```powershell
scp .\raspberry-pi\src\main.py group29@192.168.137.70:/home/group29/sciot_project/main.py
```

## 10. Run the Raspberry Pi Hardware Node

On the Raspberry Pi:

```bash
cd ~/sciot_project
source venv/bin/activate
python main.py
```

The hardware node publishes:

```text
warehouse/sensors/temperature
warehouse/sensors/humidity
warehouse/sensors/gas_status
warehouse/sensors/occupancy
warehouse/sensors/battery_status
```

The hardware node subscribes to:

```text
warehouse/actuators/fan/command
warehouse/actuators/buzzer/command
warehouse/actuators/led/command
warehouse/actuators/shutter/command
```

## 11. Run Battery Input

Battery status is entered manually because the project does not use a real battery sensor.

Open another Raspberry Pi terminal:

```bash
cd ~/sciot_project
source venv/bin/activate
python battery_input.py
```

Example values:

```text
90 -> normal battery
40 -> low battery
10 -> critical battery
```

The value is written to:

```text
runtime/battery_state.json
```

The Raspberry Pi hardware node reads this file and publishes the value to:

```text
warehouse/sensors/battery_status
```

## 12. Occupancy Input

Occupancy is controlled using the real Grove button.

```text
button press toggles occupancy between 0 and 1
```

The Raspberry Pi publishes the current occupancy to:

```text
warehouse/sensors/occupancy
```

There is no separate `occupancy_input.py` script in the final hardware version because occupancy comes from the real button.

## 13. Hardware Behaviour

### DHT Sensor

The DHT sensor provides:

```text
temperature
humidity
```

These are published to:

```text
warehouse/sensors/temperature
warehouse/sensors/humidity
```

### MQ2 Gas Sensor

The MQ2 sensor publishes:

```text
OK
ALERT
```

to:

```text
warehouse/sensors/gas_status
```

### Fan

The fan receives MQTT commands on:

```text
warehouse/actuators/fan/command
```

Example payloads:

```text
OFF
ON
40
70
```

### Buzzer

The buzzer receives commands on:

```text
warehouse/actuators/buzzer/command
```

For an `ON` command, the buzzer gives two short beeps and then turns off automatically.

### RGB LED

The RGB LED receives commands on:

```text
warehouse/actuators/led/command
```

Example payloads:

```text
GREEN
ORANGE
RED
OFF
```

### Shutter / Servo

The shutter servo receives commands on:

```text
warehouse/actuators/shutter/command
```

Example payloads:

```text
OPEN
CLOSE
HALF
```

The Raspberry Pi only executes the command it receives. The decision about whether the shutter should close is made by the laptop AI planner/problem generator.

## 14. Start Node-RED Dashboard

Node-RED runs on the Raspberry Pi.

Start Node-RED:

```bash
node-red-start
```

Open the Node-RED editor from the laptop browser:

```text
http://<RASPBERRY_PI_IP>:1880
```

Open the dashboard:

```text
http://<RASPBERRY_PI_IP>:1880/dashboard
```

Because Node-RED and Mosquitto both run on the Raspberry Pi, MQTT nodes in Node-RED should use:

```text
host: localhost
port: 1883
```

## 15. Full Raspberry Pi Run Order

### Terminal 1

```bash
sudo systemctl start mosquitto
node-red-start
```

### Terminal 2

```bash
cd ~/sciot_project
source venv/bin/activate
python main.py
```

### Terminal 3, optional battery input

```bash
cd ~/sciot_project
source venv/bin/activate
python battery_input.py
```

## 16. Manual MQTT Testing

Subscribe to all warehouse topics:

```bash
mosquitto_sub -h localhost -t "warehouse/#" -v
```

Test LED command:

```bash
mosquitto_pub -h localhost -t "warehouse/actuators/led/command" -m "GREEN"
```

Test buzzer command:

```bash
mosquitto_pub -h localhost -t "warehouse/actuators/buzzer/command" -m "ON"
```

Test shutter command:

```bash
mosquitto_pub -h localhost -t "warehouse/actuators/shutter/command" -m "OPEN"
```

## 17. Troubleshooting

### Laptop cannot connect to broker

Check the Pi IP:

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

Check port:

```bash
sudo ss -ltnp | grep 1883
```

### pigpio error

If the servo, MQ2, or RGB LED gives a pigpio connection error:

```bash
sudo systemctl start pigpiod
```

Then run the node again:

```bash
python main.py
```

### I2C / GrovePi error

If this appears:

```text
OSError: [Errno 5] Input/output error
```

Stop the running script:

```bash
sudo pkill -f main.py
```

Then physically:

```text
remove the Grove module/cable
plug it back in firmly
```

If needed, reboot:

```bash
sudo reboot
```

Then run again:

```bash
cd ~/sciot_project
source venv/bin/activate
python main.py
```

### Dashboard shows no values

Check:

```text
Mosquitto is running
Node-RED is running
Raspberry Pi hardware node is running
Node-RED MQTT broker is set to localhost:1883
dashboard topics match the project MQTT topics
```

## 18. Notes

```text
The Raspberry Pi is the MQTT broker host.
The laptop connects to the Raspberry Pi IP.
The Raspberry Pi hardware node uses localhost as the broker address.
Battery is manual/software input.
Occupancy uses the real Grove button.
The shutter decision is made by the laptop planner.
The Raspberry Pi only executes received actuator commands.
```
