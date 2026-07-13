# Notifications Setup

This README explains how manager notifications are handled.

The project uses ntfy notifications.

Notification code is located in:

```text
notifications/
├── README.md
├── __init__.py
├── ntfy_sender.py
├── notification_manager.py
└── test_notifications.py
```

## 1. Install Python Requests

From the laptop project root:

```powershell
.\venv\Scripts\activate
python -m pip install requests
```

## 2. Choose ntfy Topic

The topic is defined in:

```text
notifications/ntfy_sender.py
```

Example:

```python
NTFY_TOPIC = "smartwarehouse-group29-alerts"
```

The phone and Python code must use the same topic.

## 3. Subscribe on Phone

Install the ntfy app on the phone.

Subscribe to:

```text
smartwarehouse-group29-alerts
```

or the topic used in `ntfy_sender.py`.

## 4. Test Notification

From the project root:

```powershell
python -m notifications.test_notifications
```

Expected result:

```text
Notification appears on the phone
Terminal prints that the notification was sent
```

## 5. Notification Actions

The planner can produce these notification-related actions:

```text
notify-manager
request-evacuation
send-battery-warning
request-battery-maintenance
```

Meaning:

```text
notify-manager:
general high-risk warehouse alert

request-evacuation:
high risk with occupancy detected

send-battery-warning:
battery status is low

request-battery-maintenance:
battery status is critical
```

## 6. How Notifications Are Triggered

The AI planner generates a plan.

The plan executor reads each action.

If the action is notification-related, it calls:

```text
notifications/notification_manager.py
```

The notification manager then calls:

```text
notifications/ntfy_sender.py
```

## 7. Troubleshooting

### No notification on phone

Check:

```text
phone is subscribed to the correct topic
internet connection is available
requests package is installed
topic name in phone and Python code match
```

### Test works but full system does not

Check that the planner action appears in the generated plan.

For example:

```text
notify-manager manager-zone
request-evacuation manager-zone
send-battery-warning battery-zone
request-battery-maintenance battery-zone
```
