# SCIoT Dashboard - Node-RED

## Overview

This dashboard provides a real-time web interface for the Smart Battery Warehouse monitoring system. It is built with **Node-RED** and the **`@flowfuse/node-red-dashboard`** module (Dashboard 2), and communicates with the rest of the system through an **MQTT** broker (Mosquitto).

The dashboard displays:

- Current system state (NORMAL / WARNING / EMERGENCY)
- Live sensor readings (temperature, humidity, CO2 status)
- Historical charts (temperature and humidity over time)
- Actuator states (fan speed, buzzer, fire isolation shutter/servo)
- Notifications and evacuation alerts
- AI-generated action plan and plan history

## Architecture

```
main.py (Python backend)
   |
   |  publishes/subscribes
   v
Mosquitto (MQTT broker, localhost:1883)
   |
   |  mqtt in / mqtt out nodes
   v
Node-RED flow ("Flux 2")
   |
   |  ui-* nodes
   v
Dashboard 2 UI (http://<PI_IP>:1880/dashboard)
```

## Prerequisites

- Raspberry Pi with Raspberry Pi OS
- Node.js and npm
- Node-RED
- Mosquitto MQTT broker

## Installation

### 1. Install Mosquitto (MQTT broker)

```bash
sudo apt update
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

Check that the broker is listening on port `1883`:

```bash
sudo systemctl status mosquitto
mosquitto_sub -h localhost -t '#' -v
```

### 2. Install Node-RED (if not already installed)

```bash
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
```

### 3. Install the Dashboard 2 module

```bash
cd ~/.node-red
npm install @flowfuse/node-red-dashboard
```

Alternatively, from the Node-RED editor: **Menu > Manage palette > Install**, then search for `@flowfuse/node-red-dashboard` and click **Install**.

### 4. Restart Node-RED

```bash
node-red-stop
node-red-start
# or, if managed by systemd:
sudo systemctl restart nodered
```

### 5. Import the dashboard flow

1. Open the Node-RED editor: `http://<PI_IP>:1880`
2. **Menu > Import**
3. Paste the flow JSON (tab "Flux 2")
4. Click **Import**, then **Deploy**

### 6. Access the dashboard

```
http://<PI_IP>:1880/dashboard
```

## MQTT Topics

| Topic | Direction | Payload | Retain |
|---|---|---|---|
| `warehouse/sensors/temperature` | publish | float (deg C) | no |
| `warehouse/sensors/humidity` | publish | float (%) | no |
| `warehouse/sensors/co2` | publish | 0 or 1 | no |
| `warehouse/context/system_state` | publish | `NORMAL` \| `WARNING` \| `EMERGENCY` | yes |
| `warehouse/context/latest_plan` | publish | string (action plan) | yes |
| `warehouse/actuators/fan` | publish | int (0-100, percent) | no |
| `warehouse/actuators/buzzer` | publish | `ON` \| `OFF` | no |
| `warehouse/actuators/servo` | publish | `OPEN` \| `CLOSED` | no |

## Running the Full System

```bash
# Terminal 1: Node-RED (dashboard and broker already running as services)
node-red-start

# Terminal 2: Python backend (real sensors/actuators)
python3 main.py
```

## Known Issues and Adjustments Needed

- **Simulator vs real hardware**: the flow includes simulator groups ("Simulator - Sensors" and "Simulator - System State") that auto-publish test data every 5-15 seconds. These must be disabled once `main.py` starts publishing real sensor/actuator data on the same topics, otherwise the two sources will conflict.
- **Debug node**: the `debug 1` node is active by default. Disable it in normal operation to reduce overhead in the sidebar.
- **Retained messages**: actuator topics (`fan`, `buzzer`, `servo`) are not currently retained, so dashboard widgets will appear empty after a page refresh until a new message is published. Consider setting `retain: true` on these topics.
- **CO2 payload format**: the simulator publishes a binary flag (0 or 1) on the CO2 topic. Confirm that the real MQ-2 sensor code (`pi_direct.py`) publishes in the same format, since the "CO2 Classifier" node expects a value where `>= 1` means HIGH.
- **Broker security**: Mosquitto is currently configured without authentication or TLS. This is acceptable for local/lab use, but add a username and password (`mosquitto_passwd`) and enable TLS if the Pi will be reachable from a wider network.
- **Startup order**: Mosquitto must be running before Node-RED and `main.py` start, otherwise MQTT connections will fail.
- **Dashboard control**: the current flow is read-only (sensor/state display). There is no UI control (button, switch) wired to an `mqtt out` node to manually override actuators from the dashboard.