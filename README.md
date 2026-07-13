# Smart Battery Warehouse Monitoring and Response System

## 1. Project Overview

This project implements a Smart Battery Warehouse Monitoring and Response System.

The system monitors a battery storage warehouse, calculates the current risk level, generates an AI plan, executes actuator commands, updates a dashboard, and sends manager notifications.

Main monitored values:

```text
temperature
humidity
gas_status
occupancy
battery_status
```

Main response actions:

```text
fan control
buzzer alarm
RGB LED warning
shutter/servo control
dashboard update
manager notification
```

## 2. System Architecture

```text
Raspberry Pi
    - runs Mosquitto MQTT broker
    - runs Raspberry Pi hardware node
    - reads sensors and software input files
    - controls fan, buzzer, LED, and shutter
    - runs Node-RED dashboard server

Laptop
    - runs laptop AI controller
    - receives sensor values through MQTT
    - calculates context
    - generates PDDL problem
    - runs Fast Downward planner
    - executes plan through MQTT commands
    - sends manager notifications

Manager device
    - opens Node-RED dashboard
    - receives ntfy notifications
```

## 3. Repository Structure

```text
Smart-Battery-Warehouse/
├── README.md
│
├── config/
│   ├── __init__.py
│   ├── config.json
│   └── config_loader.py
│
├── dashboard/
│   ├── README.md
│   └── flows.json
│
├── executor/
│   ├── __init__.py
│   └── plan_executor.py
│
├── knowledge_base/
│   ├── __init__.py
│   └── warehouse_kb.py
│
├── laptop/
│   ├── README.md
│   ├── __init__.py
│   └── main.py
│
├── mqtt/
│   ├── README.md
│   ├── __init__.py
│   ├── laptop_controller.py
│   └── topics.py
│
├── notifications/
│   ├── README.md
│   ├── __init__.py
│   ├── ntfy_sender.py
│   ├── notification_manager.py
│   └── test_notifications.py
│
├── planner/
│   ├── README.md
│   ├── __init__.py
│   ├── ai_planner.py
│   ├── domain.pddl
│   └── problem_generator.py
│
├── processor/
│   ├── __init__.py
│   └── context_processor.py
│
└── raspberry-pi/
    ├── README.md
    └── src/
        ├── main.py
        ├── battery_input.py
        ├── occupancy_input.py
        ├── hardware/
        │   ├── grove_inputs.py
        │   ├── grove_outputs.py
        │   └── pi_direct.py
        └── mqtt/
            ├── rpi_hardware_node.py
            └── topics.py
```

## 4. Main Setup Order From the Beginning

Follow this order when setting up the full system.

### Step 1: Prepare the Raspberry Pi

Set up the Raspberry Pi first because it runs the MQTT broker and the hardware node.

See:

```text
raspberry-pi/README.md
```

Main tasks:

```text
1. Connect Raspberry Pi to the same network as the laptop.
2. Install/start Mosquitto MQTT broker.
3. Create the Raspberry Pi project folder.
4. Copy Raspberry Pi code to the Pi.
5. Start the Raspberry Pi hardware node.
6. Start battery and occupancy input scripts if needed.
```

### Step 2: Prepare the Laptop Controller

Set up the laptop Python environment.

See:

```text
laptop/README.md
```

Main tasks:

```text
1. Create a Python virtual environment.
2. Install required Python packages.
3. Set the Raspberry Pi broker IP in config/config.json.
4. Run the laptop controller.
```

### Step 3: Set Up the AI Planner

Set up Fast Downward and configure the planner path.

See:

```text
planner/README.md
```

Main tasks:

```text
1. Download Fast Downward.
2. Build Fast Downward.
3. Test that Fast Downward runs.
4. Add the planner path to config/config.json.
5. Test the PDDL problem generator and planner.
```

### Step 4: Set Up Notifications

Set up ntfy notifications.

See:

```text
notifications/README.md
```

Main tasks:

```text
1. Install Python requests package.
2. Choose or confirm the ntfy topic.
3. Subscribe to the topic on the phone.
4. Run the notification test.
```

### Step 5: Set Up Dashboard

Set up Node-RED and Dashboard 2 on the Raspberry Pi.

See:

```text
dashboard/README.md
```

Main tasks:

```text
1. Install/start Node-RED.
2. Install Dashboard 2.
3. Import dashboard flow.
4. Configure MQTT nodes to connect to localhost:1883.
5. Open the dashboard page from a browser.
```

### Step 6: Run the Full System

Recommended run order:

```text
1. Start Mosquitto on Raspberry Pi.
2. Start Node-RED dashboard on Raspberry Pi.
3. Start Raspberry Pi hardware node.
4. Start battery input script if needed.
5. Start occupancy input script if needed.
6. Start laptop AI controller.
7. Open dashboard.
8. Test demo scenarios.
```

## 5. Full System Run Commands

### On Raspberry Pi

Terminal 1:

```bash
sudo systemctl start mosquitto
node-red-start
```

Terminal 2:

```bash
cd ~/sciot_project
source venv/bin/activate
python main.py
```

Terminal 3, optional battery input:

```bash
cd ~/sciot_project
source venv/bin/activate
python battery_input.py
```

Terminal 4, optional occupancy input:

```bash
cd ~/sciot_project
source venv/bin/activate
python occupancy_input.py
```

### On Laptop

From the project root:

```powershell
.\venv\Scripts\activate
python -m laptop.main
```

### Open Dashboard

Use the Raspberry Pi IP:

```text
http://<RASPBERRY_PI_IP>:1880/dashboard
```

Example:

```text
http://192.168.137.70:1880/dashboard
```

## 6. Demo Scenarios

### Normal Scenario

Input:

```text
gas_status = OK
temperature < 29
humidity < 30
battery_status = 80
occupancy = 0
```

Expected result:

```text
risk_level = LOW
system_state = NORMAL
battery_condition = NORMAL
LED = GREEN
fan = OFF
buzzer = OFF
shutter = OPEN
```

### Medium Risk Scenario

Input:

```text
temperature >= 29
OR humidity >= 30
gas_status = OK
```

Expected result:

```text
risk_level = MEDIUM
system_state = WARNING
LED = ORANGE
fan = ON
buzzer = OFF
shutter = OPEN
```

### High Risk Scenario

Input:

```text
gas_status = ALERT
OR temperature >= 40
OR humidity >= 45 and occupancy = 1
```

Expected result:

```text
risk_level = HIGH
system_state = EMERGENCY
LED = RED
fan = ON
buzzer = ON
shutter = CLOSE
manager notification sent
```

### Battery Warning Scenario

Input:

```text
battery_status = 40
```

Expected result:

```text
battery_condition = LOW
send-battery-warning action appears in plan
manager receives battery warning notification
```

### Critical Battery Scenario

Input:

```text
battery_status = 10
```

Expected result:

```text
battery_condition = CRITICAL
request-battery-maintenance action appears in plan
manager receives critical battery notification
```

## 7. Important Notes

```text
Mosquitto broker runs on Raspberry Pi.
Node-RED dashboard runs on Raspberry Pi.
Raspberry Pi hardware node runs on Raspberry Pi.
Fast Downward runs on the laptop.
Laptop AI controller runs on the laptop.
Manager dashboard can be opened from any device on the same network.
```
