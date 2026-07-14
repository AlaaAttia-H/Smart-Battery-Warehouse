"""
Knowledge base for the Smart Battery Warehouse.

Stores static warehouse knowledge and runtime knowledge.
"""

from datetime import datetime

from config.config_loader import get_threshold
from mqtt import topics


# -----------------------------
# Static warehouse knowledge
# -----------------------------

ZONES = {
    "battery_zone": {
        "pddl_name": "battery-zone",
        "description": "Zone where batteries are stored and monitored.",
    },
    "manager_zone": {
        "pddl_name": "manager-zone",
        "description": "Zone where the manager dashboard, LED, and shutter are located.",
    },
}


DASHBOARDS = {
    "manager_dashboard": {
        "pddl_name": "manager-dashboard",
        "zone": "manager_zone",
        "description": "Dashboard running on the manager PC.",
    }
}


ACTUATORS = {
    "fan": {
        "topic": topics.ACTUATOR_FAN_COMMAND,
        "zone": "battery_zone",
    },
    "buzzer": {
        "topic": topics.ACTUATOR_BUZZER_COMMAND,
        "zone": "battery_zone",
    },
    "led": {
        "topic": topics.ACTUATOR_LED_COMMAND,
        "zone": "manager_zone",
    },
    "shutter": {
        "topic": topics.ACTUATOR_SHUTTER_COMMAND,
        "zone": "manager_zone",
    },
}

PLANNER_ACTION_TO_MQTT = {
    "start-fan": {
        "topic": topics.ACTUATOR_FAN_COMMAND,
        "payload": "ON",
    },
    "stop-fan": {
        "topic": topics.ACTUATOR_FAN_COMMAND,
        "payload": "OFF",
    },
    "activate-alarm": {
        "topic": topics.ACTUATOR_BUZZER_COMMAND,
        "payload": "ON",
    },
    "deactivate-alarm": {
        "topic": topics.ACTUATOR_BUZZER_COMMAND,
        "payload": "OFF",
    },
    "set-red-light": {
        "topic": topics.ACTUATOR_LED_COMMAND,
        "payload": "RED",
    },
    "set-orange-light": {
        "topic": topics.ACTUATOR_LED_COMMAND,
        "payload": "ORANGE",
    },
    "set-green-light": {
        "topic": topics.ACTUATOR_LED_COMMAND,
        "payload": "GREEN",
    },
    "open-shutter": {
        "topic": topics.ACTUATOR_SHUTTER_COMMAND,
        "payload": "OPEN",
    },
    "close-shutter": {
        "topic": topics.ACTUATOR_SHUTTER_COMMAND,
        "payload": "CLOSE",
    },
    "notify-manager": {
        "topic": topics.NOTIFICATION_MANAGER,
        "payload": "EMERGENCY: Dangerous warehouse condition detected.",
    },
    "request-evacuation": {
        "topic": topics.NOTIFICATION_MANAGER,
        "payload": "Evacuation requested because high risk was detected while occupancy is present.",
    },
    "send-battery-warning": {
        "topic": topics.NOTIFICATION_MANAGER,
        "payload": "Battery level is low. Manager warning sent.",
    },
    "request-battery-maintenance": {
        "topic": topics.NOTIFICATION_MANAGER,
        "payload": "Battery condition is critical. Maintenance is required.",
    },
}


# -----------------------------
# Runtime knowledge
# -----------------------------

CURRENT_STATE = {
    "temperature": None,
    "humidity": None,
    "gas_status": "OK",
    "occupancy": 0,
    "battery_status": 100,
    "risk_level": "UNKNOWN",
    "battery_condition": "NORMAL",
}

SENSOR_HISTORY = []
LATEST_PLAN = []

MAX_HISTORY_LENGTH = 50


def now():
    return datetime.now().isoformat(timespec="seconds")


def get_zone_pddl_name(zone_key):
    return ZONES[zone_key]["pddl_name"]


def get_dashboard_pddl_name(dashboard_key):
    return DASHBOARDS[dashboard_key]["pddl_name"]


def get_temperature_medium_threshold():
    return float(get_threshold("temperature_medium"))


def get_temperature_high_threshold():
    return float(get_threshold("temperature_high"))


def get_humidity_medium_threshold():
    return float(get_threshold("humidity_medium"))


def get_humidity_high_threshold():
    return float(get_threshold("humidity_high"))


def get_battery_low_threshold():
    return int(get_threshold("battery_low"))


def get_battery_critical_threshold():
    return int(get_threshold("battery_critical"))


def update_sensor_value(sensor_name, value):
    CURRENT_STATE[sensor_name] = value

    SENSOR_HISTORY.append({
        "timestamp": now(),
        "sensor": sensor_name,
        "value": value,
    })

    while len(SENSOR_HISTORY) > MAX_HISTORY_LENGTH:
        SENSOR_HISTORY.pop(0)

def get_action_mapping(action_name):
    return PLANNER_ACTION_TO_MQTT.get(action_name)

def update_current_state(key, value):
    CURRENT_STATE[key] = value


def get_current_state():
    return CURRENT_STATE


def set_latest_plan(plan):
    global LATEST_PLAN
    LATEST_PLAN = list(plan)


def get_latest_plan():
    return LATEST_PLAN