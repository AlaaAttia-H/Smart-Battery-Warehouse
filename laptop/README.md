# Laptop Controller Setup

This README explains how to set up and run the laptop side of the project.

The laptop runs:

```text
MQTT laptop controller
context processor
PDDL problem generator
Fast Downward planner
plan executor
notification manager
```

## 1. Open the Project Folder

Open the project root in VS Code or PowerShell:

```powershell
cd "<PATH_TO_PROJECT>/Smart-Battery-Warehouse"
```

Example:

```powershell
cd "C:\Users\<YOUR_USERNAME>\Documents\Smart-Battery-Warehouse"
```

## 2. Create Virtual Environment

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\activate
```

## 3. Install Required Packages

```powershell
python -m pip install --upgrade pip
python -m pip install paho-mqtt requests
```

## 4. Configure Raspberry Pi Broker IP

Edit:

```text
config/config.json
```

Set the Raspberry Pi IP:

```json
"mqtt": {
  "broker_host": "<RASPBERRY_PI_IP>",
  "broker_port": 1883
}
```

Example:

```json
"mqtt": {
  "broker_host": "192.168.137.70",
  "broker_port": 1883
}
```

## 5. Run the Laptop Controller

From the project root:

```powershell
.\venv\Scripts\activate
python laptop/src/main.py
```

The controller will:

```text
subscribe to sensor topics
calculate risk level and battery condition
publish context topics
generate PDDL problem
run planner
publish current and last plans
execute MQTT actuator commands
send notifications
```

## 6. Important

Run the controller from the project root.

Use:

```powershell
python laptop/src/main.py
```

Do not run package files directly like:

```powershell
python mqtt/laptop_controller.py
```

because that can cause import errors.
