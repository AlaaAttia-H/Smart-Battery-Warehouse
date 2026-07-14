# Smart Battery Warehouse Monitoring and Response System

## Overview

This project implements a Smart Battery Warehouse Monitoring and Response System using:

```text
IoT sensing
MQTT communication
AI planning
automatic actuator control
dashboard visualisation
manager notifications
```

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

## Main System Structure

```text
Smart-Battery-Warehouse/
├── README.md
├── laptop/
│   ├── README.md
│   └── src/
├── raspberry-pi/
│   ├── README.md
│   └── src/
├── dashboard/
│   ├── README.md
│   └── flows.json
└── docs/component README files
```

## Where to Find Setup Instructions

This root README gives only the general overview.  
For detailed setup and running instructions, use the README file inside each component folder.

### Raspberry Pi Setup

Use:

```text
raspberry-pi/README.md
```

This explains:

```text
Raspberry Pi connection
Mosquitto setup
pigpio setup
copying Raspberry Pi files
running the hardware node
battery input
Grove button occupancy
I2C troubleshooting
manual MQTT tests
```

### Laptop Controller Setup

Use:

```text
laptop/README.md
```

This explains:

```text
Python virtual environment
MQTT broker IP configuration
running the laptop AI controller
context signature
replanning logic
```

### AI Planner Setup

Use:

```text
laptop/src/planner/README.md
```

This explains:

```text
Fast Downward download and setup
PDDL domain and problem files
problem_generator.py logic
planner testing
HIGH/MEDIUM/LOW planning rules
shutter planning based on occupancy
```

### Executor Explanation

Use:

```text
laptop/src/executor/README.md
```

This explains:

```text
how planner actions are executed
how MQTT commands are published
why the executor stays generic
```

### Knowledge Base Explanation

Use:

```text
laptop/src/knowledge_base/README.md
```

This explains:

```text
planner action to MQTT mappings
warehouse zones
notification meanings
threshold access
```

### MQTT Topics

Use:

```text
laptop/src/mqtt/README.md
```

or the MQTT README in the project docs, depending on the final folder structure.

This explains:

```text
sensor topics
context topics
planning topics
notification topics
actuator command topics
example payloads
```

### Notifications Setup

Use:

```text
laptop/src/notifications/README.md
```

This explains:

```text
ntfy setup
notification topic
notification testing
notification action meanings
```

### Dashboard Setup

Use:

```text
dashboard/README.md
```

This explains:

```text
Node-RED setup
Dashboard 2 installation
importing flows.json
dashboard MQTT topics
opening the dashboard page
```

## Main Component Responsibilities

### Raspberry Pi

```text
runs Mosquitto MQTT broker
runs the hardware node
reads DHT temperature/humidity
reads MQ2 gas status
reads Grove button occupancy
reads battery value from JSON input
controls fan, buzzer, RGB LED, and shutter/servo
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

## Final Behaviour Summary

### Normal

```text
risk_level = LOW
LED = GREEN
fan = OFF
buzzer = OFF
shutter = OPEN
```

### Medium Risk

```text
risk_level = MEDIUM
LED = ORANGE
fan = ON
buzzer = OFF
shutter = OPEN
```

### High Risk With Occupancy

```text
risk_level = HIGH
occupancy = 1
LED = RED
buzzer gives two short beeps
manager receives high-risk notification
evacuation notification is sent
shutter stays open
```

### High Risk Without Occupancy

```text
risk_level = HIGH
occupancy = 0
LED = RED
buzzer gives two short beeps
manager receives high-risk notification
shutter closes
```

### Battery Low

```text
battery_condition = LOW
manager receives battery warning notification
```

### Battery Critical

```text
battery_condition = CRITICAL
manager receives battery maintenance notification
```

## Full Run Order

For full detailed commands, see the component README files.

General order:

```text
1. Start Mosquitto on Raspberry Pi.
2. Start Node-RED dashboard on Raspberry Pi.
3. Start Raspberry Pi hardware node.
4. Start battery input if needed.
5. Start laptop AI controller.
6. Open dashboard.
7. Test demo scenarios.
```

## Important Notes

```text
Mosquitto broker runs on Raspberry Pi.
Raspberry Pi hardware node runs on Raspberry Pi.
Node-RED dashboard runs on Raspberry Pi.
Fast Downward runs on the laptop.
Laptop AI controller runs on the laptop.
The executor stays generic and only publishes mapped MQTT actions.
The Raspberry Pi only executes received actuator commands.
The planner/problem generator decides which actions are needed.
```