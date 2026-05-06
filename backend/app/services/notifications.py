import httpx
from app.models.alert import Alert


async def send_alert_notification(alert: Alert, event_type: str):
    print(f"Alert {event_type}: {alert.message}")
    return True


async def send_slack_notification(webhook_url: str, message: str):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(webhook_url, json={"text": message})
        except Exception as e:
            print(f"Failed to send Slack notification: {e}")


async def send_email_notification(to_email: str, subject: str, body: str):
    print(f"Email notification to {to_email}: {subject}")
    return True
