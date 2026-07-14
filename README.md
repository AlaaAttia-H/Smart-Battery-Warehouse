# Smart Battery Warehouse Monitoring and Response System

## Overview

This project implements a smart battery warehouse system using IoT sensing, MQTT communication, AI planning, actuator control, dashboard visualisation, and manager notifications.

The system monitors:

```text
temperature
humidity
gas_status
occupancy
battery_status
```

The system controls:

```text
fan
buzzer
RGB LED
shutter/servo
manager notifications
dashboard updates
```

## Final Folder Structure

```text
Smart-Battery-Warehouse/
├── README.md
├── laptop/
│   ├── README.md
│   └── src/
│       ├── main.py
│       ├── config/
│       ├── executor/
│       ├── knowledge_base/
│       ├── mqtt/
│       ├── notifications/
│       ├── planner/
│       └── processor/
├── raspberry-pi/
│   ├── README.md
│   └── src/
│       ├── main.py
│       ├── battery_input.py
│       ├── hardware/
│       └── mqtt/
└── dashboard/
    ├── README.md
    └── flows.json
```

## Component Responsibilities

### Raspberry Pi

```text
runs Mosquitto MQTT broker
runs the hardware node
reads DHT temperature/humidity
reads MQ2 gas status
reads Grove button occupancy
reads battery value from JSON input
controls fan, buzzer, RGB LED, and shutter
runs Node-RED dashboard server
```

### Laptop

```text
receives sensor values through MQTT
calculates risk level and battery condition
generates PDDL problem files
runs Fast Downward
executes planner actions through MQTT
sends ntfy notifications
publishes dashboard context and plan topics
```

### Dashboard

```text
subscribes to MQTT topics
shows live sensor values
shows risk level and system state
shows current and previous AI plans
shows notifications and actuator states
```

## Behaviour Logic

### Risk Levels

```text
LOW: normal condition
MEDIUM: temperature or humidity warning condition
HIGH: gas alert or dangerous condition
```

### Fan Logic

```text
MEDIUM risk -> fan ON
HIGH risk -> fan is not started
LOW risk -> fan OFF
```

### High Risk Logic

When `risk_level = HIGH`:

```text
buzzer gives two short beeps
LED becomes RED
manager receives high-risk notification
dashboard is updated
```

If occupancy is present:

```text
occupancy = 1
→ evacuation notification is generated
→ shutter does not close
```

If no occupancy is present:

```text
occupancy = 0
→ shutter closes
```

So the shutter closes only when:

```text
risk_level = HIGH
occupancy = 0
```

### Occupancy and Shutter Planning

This is handled in the problem generator, not in the executor.

```text
HIGH + occupancy = 1
→ do not generate close-shutter

HIGH + occupancy = 0
→ generate close-shutter
```

This keeps the components separate:

```text
problem_generator.py decides what actions are needed
executor.py only publishes MQTT commands
Raspberry Pi only executes actuator commands
```

### Buzzer Logic

The buzzer should not stay on continuously.

For a buzzer ON command:

```text
two short beeps
then automatically OFF
```

### Battery Condition

```text
NORMAL: battery_status >= 50
LOW: 20 <= battery_status < 50
CRITICAL: battery_status < 20
```

Battery notifications are separate from high-risk environmental notifications.

## Notification Meanings

```text
notify-manager: environmental high-risk alert
request-evacuation: high risk while occupancy is present
send-battery-warning: battery level is low
request-battery-maintenance: battery level is critical
```

`notify-manager` is not a generic notification. In this project, it means a HIGH risk warehouse alert.

## Full Run Order

### Raspberry Pi terminal 1

```bash
sudo systemctl start mosquitto
node-red-start
```

### Raspberry Pi terminal 2

```bash
cd ~/sciot_project
source venv/bin/activate
python main.py
```

### Raspberry Pi terminal 3, optional battery input

```bash
cd ~/sciot_project
source venv/bin/activate
python battery_input.py
```

### Laptop terminal

From the project root:

```powershell
cd laptop/src
python main.py
```

### Dashboard

```text
http://<RASPBERRY_PI_IP>:1880/dashboard
```

## Demo Scenarios

### Normal

```text
gas_status = OK
occupancy = 0
battery_status = 90
temperature and humidity normal
```

Expected:

```text
risk_level = LOW
system_state = NORMAL
LED = GREEN
fan = OFF
buzzer = OFF
shutter = OPEN
```

### Medium Risk

```text
temperature or humidity above warning threshold
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

### High Risk With Occupancy

```text
gas_status = ALERT
occupancy = 1
```

Expected:

```text
risk_level = HIGH
system_state = EMERGENCY
LED = RED
buzzer gives two beeps
manager receives high-risk notification
evacuation notification is sent
shutter stays open
```

### High Risk Without Occupancy

```text
gas_status = ALERT
occupancy = 0
```

Expected:

```text
risk_level = HIGH
system_state = EMERGENCY
LED = RED
buzzer gives two beeps
manager receives high-risk notification
shutter closes
```

### Occupancy Clears During High Risk

```text
gas_status = ALERT
occupancy changes from 1 to 0
```

Expected:

```text
laptop detects occupancy change
new PDDL problem is generated
new plan includes close-shutter
shutter closes
```

### Battery Low

```text
battery_status = 40
```

Expected:

```text
battery_condition = LOW
send-battery-warning appears in plan
manager receives battery warning
```

### Battery Critical

```text
battery_status = 10
```

Expected:

```text
battery_condition = CRITICAL
request-battery-maintenance appears in plan
manager receives critical battery notification
```
