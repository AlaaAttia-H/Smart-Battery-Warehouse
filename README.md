# Smart Battery Warehouse Monitoring and Response System

## Overview

This project monitors a battery storage warehouse using IoT sensors, MQTT communication, AI planning, automated actuator control, dashboard visualisation, and manager notifications.

Main monitored values:

- Temperature
- Humidity
- Gas status
- Occupancy
- Battery status

Main actuator/response actions:

- Fan control
- Buzzer alarm
- RGB LED warning
- Shutter/servo control
- Manager notification
- Dashboard update

## Architecture

```text
Raspberry Pi hardware node
    - reads sensors
    - reads battery/occupancy JSON inputs
    - publishes sensor values to MQTT
    - receives actuator commands
    - controls fan, buzzer, LED, and shutter

Mosquitto MQTT broker
    - runs on Raspberry Pi
    - connects Raspberry Pi, laptop controller, and dashboard

Laptop AI controller
    - receives sensor values
    - calculates risk level and battery condition
    - generates PDDL problem instances
    - runs Fast Downward planner
    - executes generated plan through MQTT commands
    - sends manager notifications

Node-RED dashboard
    - runs on Raspberry Pi
    - subscribes to MQTT topics
    - displays current state, sensor values, plans, notifications, and actuator states
```

## Main Folders

```text
config/              Configuration and thresholds
executor/            Executes generated AI plans
knowledge_base/      Static warehouse knowledge and action mappings
laptop/              Laptop entry point
mqtt/                Laptop MQTT controller and shared topics
notifications/       ntfy notification sender and notification manager
planner/             PDDL domain, problem generator, Fast Downward wrapper
processor/           Context/risk processing
raspberry-pi/src/    Raspberry Pi hardware node and input scripts
dashboard/           Node-RED dashboard flow
```

## MQTT Topics

### Sensor topics

Published by the Raspberry Pi hardware node:

```text
warehouse/sensors/temperature
warehouse/sensors/humidity
warehouse/sensors/gas_status
warehouse/sensors/occupancy
warehouse/sensors/battery_status
```

### Context/system topics

Published by the laptop AI controller:

```text
warehouse/context/risk_level
warehouse/context/system_state
warehouse/context/battery_condition
```

Payload meanings:

```text
risk_level: LOW / MEDIUM / HIGH
system_state: NORMAL / WARNING / EMERGENCY
battery_condition: NORMAL / LOW / CRITICAL
```

### Planning topics

Published by the laptop AI controller:

```text
warehouse/planning/plan
warehouse/planning/current_plan
warehouse/planning/last_plan
warehouse/planning/execution_status
```

Payload meanings:

```text
current_plan: currently generated/executed AI plan
last_plan: previous AI plan
execution_status: EXECUTING / COMPLETED / FAILED / NO_PLAN
```

### Notification topic

```text
warehouse/notifications/manager
```

### Actuator command topics

Published by the laptop AI controller and subscribed to by the Raspberry Pi:

```text
warehouse/actuators/fan/command
warehouse/actuators/buzzer/command
warehouse/actuators/led/command
warehouse/actuators/shutter/command
```

Example payloads:

```text
fan/command: OFF / 30 / 40 / 70 / ON
buzzer/command: ON / OFF
led/command: GREEN / ORANGE / RED / OFF
shutter/command: OPEN / CLOSE
```

## Risk Logic

Risk is calculated in:

```text
processor/context_processor.py
```

Recommended logic:

```text
LOW:
- gas_status = OK
- temperature < temperature_medium
- humidity < humidity_medium

MEDIUM:
- temperature >= temperature_medium
OR
- humidity >= humidity_medium

HIGH:
- gas_status = ALERT
OR
- temperature >= temperature_high
OR
- humidity >= humidity_high AND occupancy > 0
```

System state for dashboard:

```text
LOW    -> NORMAL
MEDIUM -> WARNING
HIGH   -> EMERGENCY
```

Battery condition:

```text
NORMAL:   battery_status >= 50
LOW:      20 <= battery_status < 50
CRITICAL: battery_status < 20
```

## Config

Edit:

```text
config/config.json
```

Important fields:

```json
{
  "mqtt": {
    "broker_host": "192.168.137.70",
    "broker_port": 1883
  },
  "thresholds": {
    "temperature_medium": 29.0,
    "temperature_high": 40.0,
    "humidity_medium": 30.0,
    "humidity_high": 45.0,
    "battery_low": 50,
    "battery_critical": 20
  },
  "planner": {
    "fast_downward_path": "C:/path/to/fast-downward.py",
    "plan_output_path": "planner/generated_plan.txt"
  }
}
```

Update `broker_host` whenever the Raspberry Pi IP changes.

## Raspberry Pi Setup

SSH into the Raspberry Pi:

```bash
ssh group29@192.168.137.70
```

Check the Pi IP:

```bash
hostname -I
```

Activate the project environment:

```bash
cd ~/sciot_project
source venv/bin/activate
```

Check Mosquitto:

```bash
sudo systemctl status mosquitto
```

Start Mosquitto if needed:

```bash
sudo systemctl start mosquitto
```

Enable Mosquitto on boot:

```bash
sudo systemctl enable mosquitto
```

## Copy Raspberry Pi Code from Laptop to Pi

From Windows PowerShell in the project root:

```powershell
scp .\raspberry-pi\src\main.py group29@192.168.137.70:/home/group29/sciot_project/main.py
scp .\raspberry-pi\src\battery_input.py group29@192.168.137.70:/home/group29/sciot_project/battery_input.py
scp .\raspberry-pi\src\occupancy_input.py group29@192.168.137.70:/home/group29/sciot_project/occupancy_input.py
scp .\raspberry-pi\src\mqtt\rpi_hardware_node.py group29@192.168.137.70:/home/group29/sciot_project/mqtt/rpi_hardware_node.py
scp .\raspberry-pi\src\hardware\grove_inputs.py group29@192.168.137.70:/home/group29/sciot_project/hardware/grove_inputs.py
scp .\raspberry-pi\src\hardware\grove_outputs.py group29@192.168.137.70:/home/group29/sciot_project/hardware/grove_outputs.py
scp .\raspberry-pi\src\hardware\pi_direct.py group29@192.168.137.70:/home/group29/sciot_project/hardware/pi_direct.py
```

## Run Raspberry Pi Hardware Node

On the Raspberry Pi:

```bash
cd ~/sciot_project
source venv/bin/activate
python main.py
```

This publishes sensor values and receives actuator commands.

## Run Battery Input

Open another Raspberry Pi terminal:

```bash
cd ~/sciot_project
source venv/bin/activate
python battery_input.py
```

Example values:

```text
80 -> NORMAL
45 -> LOW
15 -> CRITICAL
```

## Run Occupancy Input

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

## Laptop Setup

Create and activate the laptop virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

Install packages:

```powershell
python -m pip install paho-mqtt requests
```

## Fast Downward Setup

Open Developer PowerShell for Visual Studio 2022 or x64 Native Tools Command Prompt.

Go to the Fast Downward folder:

```powershell
cd "C:\Users\alaaa\Documents\Masters\SEM_2\SCIoT\Project\fast-downward-24.06.1.tar\fast-downward-24.06.1"
```

Build:

```powershell
py build.py
```

Test:

```powershell
py fast-downward.py --help
```

Set the path in `config/config.json`.

## Run Laptop AI Controller

From the project root on the laptop:

```powershell
.\venv\Scripts\activate
python -m laptop.main
```

Alternative:

```powershell
python -m mqtt.laptop_controller
```

The laptop controller:

1. Receives sensor values.
2. Calculates risk level and battery condition.
3. Publishes context and dashboard topics.
4. Generates a PDDL problem.
5. Runs Fast Downward.
6. Publishes current and last plan.
7. Executes the plan through MQTT.
8. Sends notifications.

## VS Code Run Button Setup

Create:

```text
.vscode/launch.json
```

Use:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run Laptop AI Controller",
      "type": "python",
      "request": "launch",
      "module": "laptop.main",
      "cwd": "${workspaceFolder}",
      "console": "integratedTerminal"
    },
    {
      "name": "Run Notification Test",
      "type": "python",
      "request": "launch",
      "module": "notifications.test_notifications",
      "cwd": "${workspaceFolder}",
      "console": "integratedTerminal"
    },
    {
      "name": "Run Problem Generator",
      "type": "python",
      "request": "launch",
      "module": "planner.problem_generator",
      "cwd": "${workspaceFolder}",
      "console": "integratedTerminal"
    },
    {
      "name": "Run AI Planner Only",
      "type": "python",
      "request": "launch",
      "module": "planner.ai_planner",
      "cwd": "${workspaceFolder}",
      "console": "integratedTerminal"
    }
  ]
}
```

## Notifications

The project uses ntfy.

Test notification:

```powershell
python -m notifications.test_notifications
```

Subscribe on the phone to:

```text
smartwarehouse-group29-alerts
```

Notification-related planner actions:

```text
notify-manager
request-evacuation
send-battery-warning
request-battery-maintenance
```

## Node-RED Dashboard Setup

Start Node-RED on the Raspberry Pi:

```bash
node-red-start
```

Open Node-RED editor:

```text
http://192.168.137.70:1880
```

Dashboard page:

```text
http://192.168.137.70:1880/dashboard
```

Install Dashboard 2 if needed:

```bash
cd ~/.node-red
npm install @flowfuse/node-red-dashboard
node-red-stop
node-red-start
```

Import the dashboard flow:

```text
Menu -> Import -> paste/import dashboard flow JSON -> Import -> Deploy
```

Dashboard should subscribe to:

```text
warehouse/sensors/temperature
warehouse/sensors/humidity
warehouse/sensors/gas_status
warehouse/sensors/occupancy
warehouse/sensors/battery_status

warehouse/context/risk_level
warehouse/context/system_state
warehouse/context/battery_condition

warehouse/planning/plan
warehouse/planning/current_plan
warehouse/planning/last_plan
warehouse/planning/execution_status

warehouse/notifications/manager

warehouse/actuators/fan/command
warehouse/actuators/buzzer/command
warehouse/actuators/led/command
warehouse/actuators/shutter/command
```

Dashboard should display:

```text
Current system status -> warehouse/context/system_state
Risk level -> warehouse/context/risk_level
Battery condition -> warehouse/context/battery_condition
Plan being executed -> warehouse/planning/current_plan
Last plan -> warehouse/planning/last_plan
Execution status -> warehouse/planning/execution_status
Latest manager notification -> warehouse/notifications/manager
```

## Full System Run Order

1. Start Mosquitto on Raspberry Pi:

```bash
sudo systemctl start mosquitto
```

2. Start Node-RED on Raspberry Pi:

```bash
node-red-start
```

3. Start Raspberry Pi hardware node:

```bash
cd ~/sciot_project
source venv/bin/activate
python main.py
```

4. Start battery input:

```bash
cd ~/sciot_project
source venv/bin/activate
python battery_input.py
```

5. Start occupancy input:

```bash
cd ~/sciot_project
source venv/bin/activate
python occupancy_input.py
```

6. Start laptop AI controller:

```powershell
cd "C:\Users\alaaa\Documents\Masters\SEM_2\SCIoT\Project\Smart-Battery-Warehouse"
.\venv\Scripts\activate
python -m laptop.main
```

7. Open dashboard:

```text
http://192.168.137.70:1880/dashboard
```

## Demo Scenarios

### Normal

```text
gas_status = OK
temperature < 29
humidity < 30
battery_status = 80
occupancy = 0
```

Expected:

```text
risk_level = LOW
system_state = NORMAL
battery_condition = NORMAL
LED = GREEN
fan = OFF
buzzer = OFF
shutter = OPEN
```

### Medium Risk

```text
temperature >= 29
OR humidity >= 30
gas_status = OK
```

Expected:

```text
risk_level = MEDIUM
system_state = WARNING
LED = ORANGE
fan = ON
buzzer = OFF
shutter = OPEN
```

### High Risk

```text
gas_status = ALERT
OR temperature >= 40
OR humidity >= 45 and occupancy = 1
```

Expected:

```text
risk_level = HIGH
system_state = EMERGENCY
LED = RED
fan = ON
buzzer = ON
shutter = CLOSE
manager notification sent
```

### Battery Warning

```text
battery_status = 40
```

Expected:

```text
battery_condition = LOW
send-battery-warning action appears in plan
manager receives battery warning
```

### Critical Battery

```text
battery_status = 10
```

Expected:

```text
battery_condition = CRITICAL
request-battery-maintenance action appears in plan
manager receives critical battery notification
```

## Troubleshooting

### Import errors in VS Code

Run from the project root:

```powershell
python -m laptop.main
```

Do not run package files directly like:

```powershell
python mqtt/laptop_controller.py
```

### Fast Downward not found

Check `fast_downward_path` in:

```text
config/config.json
```

### Laptop cannot connect to MQTT

Check Pi IP:

```bash
hostname -I
```

Check Mosquitto:

```bash
sudo systemctl status mosquitto
```

Restart if needed:

```bash
sudo systemctl restart mosquitto
```

### GrovePi I2C errors

If this appears:

```text
OSError: [Errno 5] Input/output error
```

stop running scripts and reboot:

```bash
sudo pkill -f main.py
sudo pkill -f test_button
sudo reboot
```

For the final demo, occupancy is handled through JSON input to avoid repeated GrovePi button polling.

### Dashboard shows fake values

Disable simulator nodes in Node-RED and make sure the dashboard subscribes to the current project topics.

## Git Workflow

Recommended safe workflow:

```powershell
git checkout -b alaa-integration-final
git add .
git commit -m "Integrate AI planner notifications and dashboard topics"
git push -u origin alaa-integration-final

git fetch origin
git merge origin/main

# Resolve conflicts if needed
git add .
git commit -m "Resolve conflicts with latest main"

git checkout main
git pull origin main
git merge alaa-integration-final
git push origin main
```

## Notes

- Mosquitto runs on the Raspberry Pi.
- Node-RED dashboard runs on the Raspberry Pi.
- Laptop AI controller runs on the laptop.
- Fast Downward runs on the laptop.
- Sensor values are published by the Raspberry Pi.
- Planning and actuator decisions are made on the laptop.
- Actuator commands are sent back to the Raspberry Pi through MQTT.
- Dashboard subscribes to MQTT topics and visualises the system.
