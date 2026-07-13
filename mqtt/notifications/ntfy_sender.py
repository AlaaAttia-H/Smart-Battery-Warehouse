import requests

NTFY_TOPIC = "smartwarehouse-group29-alerts"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"


def send_ntfy_notification(title, message, priority="high"):
    headers = {
        "Title": title,
        "Priority": priority,
        "Tags": "warning"
    }

    try:
        response = requests.post(
            NTFY_URL,
            data=message.encode("utf-8"),
            headers=headers
        )

        if response.status_code == 200:
            print("[NTFY] Notification sent")
        else:
            print("[NTFY ERROR]", response.text)

    except Exception as e:
        print("[NTFY ERROR]", e)