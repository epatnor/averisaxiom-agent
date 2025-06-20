# === File: daily_report.py ===
import sqlite3
import smtplib
from email.mime.text import MIMEText
from config import Config
import os

def update_stats():
    db_path = os.getenv("DATABASE_PATH", "data/posts.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(like_count), SUM(repost_count), SUM(reply_count) FROM posts WHERE status = 'published'")
    total_published, total_likes, total_reposts, total_replies = c.fetchone()
    conn.close()

    total_likes = total_likes or 0
    total_reposts = total_reposts or 0
    total_replies = total_replies or 0

    return total_published, total_likes, total_reposts, total_replies

def generate_report():
    total_published, total_likes, total_reposts, total_replies = update_stats()
    report = (
        f"AverisAxiom Daily Report:\n\n"
        f"Total Published: {total_published}\n"
        f"Total Likes: {total_likes}\n"
        f"Total Reposts: {total_reposts}\n"
        f"Total Replies: {total_replies}\n"
    )
    return report

def send_email(report):
    msg = MIMEText(report)
    msg['Subject'] = 'AverisAxiom Daily Report'
    msg['From'] = Config.EMAIL_FROM
    msg['To'] = Config.EMAIL_TO

    with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
        server.ehlo()
        server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    print("Generating daily report...")
    report = generate_report()
    print(report)
    print("Sending email...")
    send_email(report)
    print("Done.")
