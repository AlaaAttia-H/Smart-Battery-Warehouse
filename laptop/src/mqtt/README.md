# MQTT Topics

This README lists the MQTT topics used in the project.

## Sensor Topics

Published by Raspberry Pi:

```text
warehouse/sensors/temperature
warehouse/sensors/humidity
warehouse/sensors/gas_status
warehouse/sensors/occupancy
warehouse/sensors/battery_status
```

## Context Topics

Published by laptop controller:

```text
warehouse/context/risk_level
warehouse/context/system_state
warehouse/context/battery_condition
```

## Planning Topics

Published by laptop controller:

```text
warehouse/planning/plan
warehouse/planning/current_plan
warehouse/planning/last_plan
warehouse/planning/execution_status
```

## Notification Topic

```text
warehouse/notifications/manager
```

## Actuator Command Topics

Published by laptop controller and subscribed to by Raspberry Pi:

```text
warehouse/actuators/fan/command
warehouse/actuators/buzzer/command
warehouse/actuators/led/command
warehouse/actuators/shutter/command
```

## Example Payloads

```text
warehouse/sensors/gas_status -> OK / ALERT
warehouse/sensors/occupancy -> 0 / 1
warehouse/context/risk_level -> LOW / MEDIUM / HIGH
warehouse/context/system_state -> NORMAL / WARNING / EMERGENCY
warehouse/context/battery_condition -> NORMAL / LOW / CRITICAL
warehouse/actuators/fan/command -> OFF / 40 / ON
warehouse/actuators/buzzer/command -> ON / OFF
warehouse/actuators/led/command -> GREEN / ORANGE / RED / OFF
warehouse/actuators/shutter/command -> OPEN / CLOSE
```
