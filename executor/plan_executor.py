"""
Plan executor for the Smart Battery Warehouse.

This component executes AI planner actions.
It publishes MQTT commands and delegates notifications
to the notification manager.
"""

import time

from knowledge_base import warehouse_kb as kb
from notifications.notification_manager import send_notification_for_action


def execute_plan(plan, mqtt_client):
    if not plan:
        print("[EXECUTOR] Empty plan. Nothing to execute.")
        return

    print("[EXECUTOR] Executing AI plan...")

    for step in plan:
        step = step.strip().lower()
        parts = step.split()

        if not parts:
            continue

        action_name = parts[0]

        print(f"[EXECUTOR] Action: {step}")

        if action_name == "update-dashboard":
            print("[EXECUTOR] Dashboard update is handled by MQTT context and plan topics.")
            continue

        mapping = kb.get_action_mapping(action_name)

        if mapping is None:
            print(f"[EXECUTOR WARNING] No MQTT mapping for action: {action_name}")
            continue

        topic = mapping["topic"]
        payload = mapping["payload"]

        mqtt_client.publish(topic, payload)
        print(f"[MQTT COMMAND] {topic} -> {payload}")

        send_notification_for_action(
            action_name=action_name,
            message=payload,
        )

        time.sleep(0.2)