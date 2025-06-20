# === File: daily_report.py ===
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def update_stats():
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(like_count), SUM(repost_count), SUM(reply_count) FROM posts WHERE status = 'published'")
    total_published, total_likes, total_reposts, total_replies = c.fetchone()
    conn.close()

    total_likes = total_likes or 0
    total_reposts = total_reposts or 0
    total_replies = total_replies or 0

    return total_published, total_likes, total_reposts, total_replies

def generate_report():
    print("Generating daily report...")
    print("Updating stats from database...")
    total_published, total_likes, total_reposts, total_replies = update_stats()

    report = (
        f"AverisAxiom Daily Report\n\n"
        f"Total Published Posts: {total_published}\n"
        f"Total Likes: {total_likes}\n"
        f"Total Reposts: {total_reposts}\n"
        f"Total Replies: {total_replies}\n"
    )
    return report

def send_email(report_text):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM", smtp_user)
    email_to = os.getenv("EMAIL_TO")

    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = "AverisAxiom Daily Report"

    msg.attach(MIMEText(report_text, 'plain'))

    server = smtplib.SMTP()
    server.connect(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.send_message(msg)
    server.quit()

if __name__ == "__main__":
    report = generate_report()
    send_email(report)
    print("Daily report email sent.")
