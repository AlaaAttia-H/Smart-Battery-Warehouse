"""
MQTT topic names for the project.
"""

# Sensor topics
SENSOR_TEMPERATURE = "warehouse/sensors/temperature"
SENSOR_HUMIDITY = "warehouse/sensors/humidity"
SENSOR_CO2 = "warehouse/sensors/co2"
SENSOR_OCCUPANCY = "warehouse/sensors/occupancy"
SENSOR_BATTERY_STATUS = "warehouse/sensors/battery_status"
SENSOR_GAS_ALERT = "warehouse/sensors/gas_alert"

SENSOR_TOPICS = [
    SENSOR_TEMPERATURE,
    SENSOR_HUMIDITY,
    SENSOR_CO2,
    SENSOR_OCCUPANCY,
    SENSOR_BATTERY_STATUS,
    SENSOR_GAS_ALERT,
]

# Actuator command topics
ACTUATOR_FAN_COMMAND = "warehouse/actuators/fan/command"
ACTUATOR_BUZZER_COMMAND = "warehouse/actuators/buzzer/command"
ACTUATOR_LED_COMMAND = "warehouse/actuators/led/command"
ACTUATOR_SHUTTER_COMMAND = "warehouse/actuators/shutter/command"

ACTUATOR_COMMAND_TOPICS = [
    ACTUATOR_FAN_COMMAND,
    ACTUATOR_BUZZER_COMMAND,
    ACTUATOR_LED_COMMAND,
    ACTUATOR_SHUTTER_COMMAND,
]

# Context, planning, and notification topics
CONTEXT_RISK_LEVEL = "warehouse/context/risk_level"
PLANNING_PLAN = "warehouse/planning/plan"
NOTIFICATION_MANAGER = "warehouse/notifications/manager"