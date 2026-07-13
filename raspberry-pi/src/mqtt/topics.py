"""
MQTT topic names for the Smart Battery Warehouse project.
"""

# Sensor topics
SENSOR_TEMPERATURE = "warehouse/sensors/temperature"
SENSOR_HUMIDITY = "warehouse/sensors/humidity"
SENSOR_GAS_STATUS = "warehouse/sensors/gas_status"
SENSOR_OCCUPANCY = "warehouse/sensors/occupancy"
SENSOR_BATTERY_STATUS = "warehouse/sensors/battery_status"

SENSOR_TOPICS = [
    SENSOR_TEMPERATURE,
    SENSOR_HUMIDITY,
    SENSOR_GAS_STATUS,
    SENSOR_OCCUPANCY,
    SENSOR_BATTERY_STATUS,
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

# Dashboard / system state topics
CONTEXT_SYSTEM_STATE = "warehouse/context/system_state"

PLANNING_CURRENT_PLAN = "warehouse/planning/current_plan"
PLANNING_LAST_PLAN = "warehouse/planning/last_plan"
PLANNING_EXECUTION_STATUS = "warehouse/planning/execution_status"