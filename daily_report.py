# === File: daily_report.py ===
import sqlite3
import smtplib
from email.mime.text import MIMEText
import os

# --- CONFIG ---
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# --- FUNCTIONS ---
def update_stats():
    conn = sqlite3.connect("/mnt/data/posts.db")
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
    total_published, total_likes, total_reposts, total_replies = update_stats()

    report = f"""
AverisAxiom Daily Report
------------------------
Total Published: {total_published}
Total Likes: {total_likes}
Total Reposts: {total_reposts}
Total Replies: {total_replies}
"""
    return report

def send_email(report):
    print("Sending email...")
    msg = MIMEText(report)
    msg["Subject"] = "AverisAxiom Daily Report"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    report = generate_report()
    send_email(report())
