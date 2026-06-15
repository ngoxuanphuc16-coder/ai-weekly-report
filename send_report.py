"""
Email sender for weekly AI/Tech Intelligence Report.
Usage: python send_report.py <path_to_html_file>
Credentials loaded from environment variables.
"""

import smtplib
import sys
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def send_html_email(html_path: str) -> None:
    html_file = Path(html_path)
    if not html_file.exists():
        raise FileNotFoundError(f"HTML report not found: {html_path}")

    smtp_user = os.environ.get("SMTP_USER", "")
    app_password = os.environ.get("SMTP_APP_PASSWORD", "")
    recipient = os.environ.get("RECIPIENT_EMAIL", "ngoxuanphuc16@gmail.com")
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))

    if not smtp_user or not app_password:
        raise ValueError("SMTP_USER and SMTP_APP_PASSWORD environment variables are required")

    html_content = html_file.read_text(encoding="utf-8")

    now = datetime.now()
    week_num = now.isocalendar()[1]
    date_str = now.strftime("%d/%m/%Y")
    subject = f"Bao Cao AI & Cong Nghe Tuan {week_num} - {date_str}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    print(f"[send] Connecting to {smtp_host}:{smtp_port}...")
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, app_password)
        server.sendmail(smtp_user, [recipient], msg.as_string())

    print(f"[send] Email sent to {recipient} — Subject: {subject}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python send_report.py <path_to_html_file>")
        sys.exit(1)
    try:
        send_html_email(sys.argv[1])
    except Exception as e:
        print(f"[send] ERROR: {e}", file=sys.stderr)
        sys.exit(1)
