from notifications.ntfy_sender import send_ntfy_notification

send_ntfy_notification(
    title="Test Notification",
    message="This is a dummy notification from Python.",
    priority="high",
)

print("Notification sent!")