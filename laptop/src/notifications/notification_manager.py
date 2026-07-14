"""
Notification manager for the Smart Battery Warehouse.

This component decides which planner actions should trigger
manager/mobile notifications.
"""

from notifications.ntfy_sender import send_ntfy_notification


NOTIFICATION_RULES = {
    "notify-manager": {
        "title": "Smart Warehouse Alert",
        "priority": "high",
    },
    "request-evacuation": {
        "title": "Evacuation Requested",
        "priority": "high",
    },
    "send-battery-warning": {
        "title": "Battery Warning",
        "priority": "default",
    },
    "request-battery-maintenance": {
        "title": "Critical Battery Condition",
        "priority": "default",
    },
}


def is_notification_action(action_name):
    return action_name in NOTIFICATION_RULES


def send_notification_for_action(action_name, message):
    if not is_notification_action(action_name):
        return

    rule = NOTIFICATION_RULES[action_name]

    send_ntfy_notification(
        title=rule["title"],
        message=message,
        priority=rule["priority"],
    )