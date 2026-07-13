# Dashboard Setup

This README explains how to set up the Node-RED dashboard.

The dashboard runs on the Raspberry Pi.

## 1. Start Node-RED

On the Raspberry Pi:

```bash
node-red-start
```

Open the Node-RED editor from a browser:

```text
http://<RASPBERRY_PI_IP>:1880
```

Example:

```text
http://192.168.137.70:1880
```

## 2. Install Dashboard 2

On the Raspberry Pi:

```bash
cd ~/.node-red
npm install @flowfuse/node-red-dashboard
```

Restart Node-RED:

```bash
node-red-stop
node-red-start
```

## 3. Import Dashboard Flow

In the Node-RED editor:

```text
Menu
-> Import
-> paste or upload dashboard/flows.json
-> Import
-> Deploy
```

## 4. MQTT Broker Setting in Node-RED

Because Node-RED runs on the Raspberry Pi and Mosquitto also runs on the Raspberry Pi, MQTT nodes should use:

```text
Broker host: localhost
Port: 1883
```

## 5. Dashboard URL

Open:

```text
http://<RASPBERRY_PI_IP>:1880/dashboard
```

Example:

```text
http://192.168.137.70:1880/dashboard
```

## 6. Dashboard Topics

The dashboard should subscribe to these topics.

Sensor topics:

```text
warehouse/sensors/temperature
warehouse/sensors/humidity
warehouse/sensors/gas_status
warehouse/sensors/occupancy
warehouse/sensors/battery_status
```

Context topics:

```text
warehouse/context/risk_level
warehouse/context/system_state
warehouse/context/battery_condition
```

Planning topics:

```text
warehouse/planning/plan
warehouse/planning/current_plan
warehouse/planning/last_plan
warehouse/planning/execution_status
```

Notification topic:

```text
warehouse/notifications/manager
```

Actuator command topics:

```text
warehouse/actuators/fan/command
warehouse/actuators/buzzer/command
warehouse/actuators/led/command
warehouse/actuators/shutter/command
```

## 7. Dashboard Display

The dashboard should display:

```text
temperature
humidity
gas status
occupancy
battery status
risk level
system state
battery condition
current AI plan
last AI plan
plan execution status
latest manager notification
actuator commands/states
```

## 8. Disable Simulator Nodes

If the dashboard has simulator nodes, disable them for the final system.

The dashboard should display real MQTT values from the Raspberry Pi and laptop controller, not fake values.

## 9. Troubleshooting

### Dashboard does not update

Check:

```text
Node-RED is running
Mosquitto is running
MQTT broker in Node-RED is localhost:1883
laptop controller is publishing context and planning topics
Raspberry Pi hardware node is publishing sensor topics
```

### Dashboard shows old topics

Make sure the dashboard uses:

```text
warehouse/sensors/gas_status
warehouse/context/system_state
warehouse/planning/current_plan
```

Do not use old topics like:

```text
warehouse/sensors/co2
warehouse/context/latest_plan
warehouse/actuators/fan
```
