# === File: daily_report.py ===
import sqlite3
from config import Config
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def update_stats():
    conn = sqlite3.connect(Config.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(like_count), SUM(repost_count), SUM(reply_count) FROM posts WHERE status = 'published'")
    total_published, total_likes, total_reposts, total_replies = c.fetchone()
    conn.close()
    return total_published or 0, total_likes or 0, total_reposts or 0, total_replies or 0

def generate_report():
    print("Generating daily report...")
    total_published, total_likes, total_reposts, total_replies = update_stats()
    report = (
        f"Daily Bluesky Report\n"
        f"======================\n"
        f"Total Published Posts: {total_published}\n"
        f"Total Likes: {total_likes}\n"
        f"Total Reposts: {total_reposts}\n"
        f"Total Replies: {total_replies}\n"
    )
    return report

def send_email(report):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM", smtp_username)
    email_to = os.getenv("EMAIL_TO")

    message = MIMEMultipart()
    message["From"] = email_from
    message["To"] = email_to
    message["Subject"] = "Daily Bluesky Report"
    message.attach(MIMEText(report, "plain"))

    if smtp_port == 465:
        # SSL connection
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(email_from, email_to, message.as_string())
    else:
        # StartTLS connection (default)
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_username, smtp_password)
            server.sendmail(email_from, email_to, message.as_string())

def main():
    report = generate_report()
    send_email(report)

if __name__ == "__main__":
    main()
