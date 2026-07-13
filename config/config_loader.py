"""
Configuration loader for the Smart Battery Warehouse.
"""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config" / "config.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


CONFIG = load_config()


def get_mqtt_broker_host():
    return CONFIG["mqtt"]["broker_host"]


def get_mqtt_broker_port():
    return int(CONFIG["mqtt"]["broker_port"])


def get_threshold(name):
    return CONFIG["thresholds"][name]

def get_planner_path():
    return CONFIG["planner"]["fast_downward_path"]


def get_plan_output_path():
    return CONFIG["planner"]["plan_output_path"]
