"""
Context processor for the Smart Battery Warehouse.

Converts raw MQTT sensor values into symbolic context for the AI planner.
"""

from knowledge_base import warehouse_kb as kb


def get_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def get_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def calculate_risk_level(temperature, humidity, gas_status, occupancy):
    gas_status = str(gas_status).upper()

    temp_medium = kb.get_temperature_medium_threshold()
    temp_high = kb.get_temperature_high_threshold()

    hum_medium = kb.get_humidity_medium_threshold()
    hum_high = kb.get_humidity_high_threshold()

    if gas_status == "ALERT":
        return "HIGH"

    if temperature >= temp_high and occupancy > 0:
        return "HIGH"

    if humidity >= hum_high and occupancy > 0:
        return "HIGH"

    if temperature >= temp_medium:
        return "MEDIUM"

    if humidity >= hum_medium:
        return "MEDIUM"

    return "LOW"


def calculate_battery_condition(battery_status):
    battery_low = kb.get_battery_low_threshold()
    battery_critical = kb.get_battery_critical_threshold()

    if battery_status < battery_critical:
        return "CRITICAL"

    if battery_status < battery_low:
        return "LOW"

    return "NORMAL"


def calculate_context(sensor_state):
    temperature = get_float(sensor_state.get("temperature"), default=0.0)
    humidity = get_float(sensor_state.get("humidity"), default=0.0)
    gas_status = str(sensor_state.get("gas_status", "OK")).upper()
    occupancy = get_int(sensor_state.get("occupancy"), default=0)
    battery_status = get_int(sensor_state.get("battery_status"), default=100)

    risk_level = calculate_risk_level(
        temperature=temperature,
        humidity=humidity,
        gas_status=gas_status,
        occupancy=occupancy,
    )

    battery_condition = calculate_battery_condition(battery_status)

    context = {
        "temperature": temperature,
        "humidity": humidity,
        "gas_status": gas_status,
        "occupancy": occupancy,
        "battery_status": battery_status,
        "risk_level": risk_level,
        "battery_condition": battery_condition,
    }

    # Store current runtime state in the knowledge base
    kb.update_current_state("temperature", temperature)
    kb.update_current_state("humidity", humidity)
    kb.update_current_state("gas_status", gas_status)
    kb.update_current_state("occupancy", occupancy)
    kb.update_current_state("battery_status", battery_status)
    kb.update_current_state("risk_level", risk_level)
    kb.update_current_state("battery_condition", battery_condition)

    return context