import json
from celery import Celery
from datetime import datetime
from urllib.parse import urlparse
import ssl
import socket
import whois
import requests
import csv
import os
import smtplib
from email.message import EmailMessage

# ----------------------- Configurable Settings ------------------------
EMAIL_ALERTS = True
EMAIL_SENDER = "hamisishehe@gmail.com"
EMAIL_PASSWORD = "cbxt ugsr cxob ryyx"
EMAIL_RECEIVER = "hamisinuru83@gmail.com"
ALERT_SSL_DAYS_LEFT = 7
LOG_FILE = "website_monitor_log.csv"
link = (
    "https://hooks.slack.com/services/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"
)
WEBSITES = [
    "https://www.google.com",
    "https://expired.badssl.com",
    "https://example.com",
]
# ----------------------------------------------------------------------
SEND_SLACK_ALERTS = True
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"  # <-- Replace with your actual webhook URL

# Celery config
celery = Celery(__name__, broker="redis://localhost:6379/0")
celery.conf.beat_schedule = {
    "monitor-every-5-minutes": {
        "task": "tasks.run_monitoring_all",
        "schedule": 300.0,  # every 5 minutes
    }
}
celery.conf.timezone = "UTC"


@celery.task
def run_monitoring_all():
    for url in WEBSITES:
        monitor_website(url)


def monitor_website(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    print(f"\nMonitoring: {url}")
    print("=" * 60)

    status = check_website(url)
    ssl_info = get_ssl_info(hostname)
    domain_expiry = get_domain_expiry(hostname)

    # Console
    for k, v in status.items():
        print(f"{k.replace('_', ' ').capitalize():25}: {v}")
    for k, v in ssl_info.items():
        print(f"{k.replace('_', ' ').capitalize():25}: {v}")
    print(f"{'Domain expiry':25}: {domain_expiry}")

    # Alerts
    if status.get("status") == "DOWN":
        send_email(
            f"ALERT: {url} is DOWN", f"Website {url} is currently not reachable."
        )
        send_email(
            f"ALERT: {url} is DOWN", f"Website {url} is currently not reachable."
        )

    if isinstance(ssl_info.get("valid_until"), datetime):
        days_left = (ssl_info["valid_until"] - datetime.utcnow()).days
        if days_left < ALERT_SSL_DAYS_LEFT:
            send_email(
                f"ALERT: SSL Expiring Soon for {hostname}",
                f"The SSL certificate for {hostname} expires in {days_left} days.",
            )

    # Log
    log_data = {
        "url": url,
        "status": status.get("status"),
        "status_code": status.get("status_code"),
        "response_time_ms": status.get("response_time_ms"),
        "ssl_valid_until": ssl_info.get("valid_until"),
        "domain_expiry": domain_expiry,
        "timestamp": datetime.utcnow(),
    }
    log_to_csv(log_data)


def check_website(url):
    try:
        response = requests.get(url, timeout=5)
        return {
            "status": "UP",
            "status_code": response.status_code,
            "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2),
            "server": response.headers.get("Server", "Unknown"),
            "content_length": len(response.content),
        }
    except requests.RequestException as e:
        return {"status": "DOWN", "error": str(e)}


def get_ssl_info(hostname):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                start_date = datetime.strptime(
                    cert["notBefore"], "%b %d %H:%M:%S %Y %Z"
                )
                expire_date = datetime.strptime(
                    cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
                )
                return {"valid_from": start_date, "valid_until": expire_date}
    except Exception as e:
        return {"error": f"SSL check failed: {e}"}


def get_domain_expiry(hostname):
    try:
        domain_info = whois.whois(hostname)
        return domain_info.expiration_date
    except Exception as e:
        return f"WHOIS failed: {e}"


def send_email(subject, body):
    if not EMAIL_ALERTS:
        return
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_slack_alert(message):
    if not SEND_SLACK_ALERTS or not SLACK_WEBHOOK_URL:
        return
    try:
        payload = {"text": message}
        response = requests.post(
            SLACK_WEBHOOK_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        if response.status_code != 200:
            print(f"Slack alert failed: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Slack alert exception: {e}")


def log_to_csv(data):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
