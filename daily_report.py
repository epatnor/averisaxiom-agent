import sqlite3
import smtplib
from email.mime.text import MIMEText
import os

DB_PATH = "/mnt/data/posts.db"

def update_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(like_count), SUM(repost_count), SUM(reply_count) FROM posts WHERE status = 'published'")
    total_published, total_likes, total_reposts, total_replies = c.fetchone()
    conn.close()
    return total_published or 0, total_likes or 0, total_reposts or 0, total_replies or 0

def generate_report():
    total_published, total_likes, total_reposts, total_replies = update_stats()
    report = f"""
AverisAxiom Daily Report:

Total Published Posts: {total_published}
Total Likes: {total_likes}
Total Reposts: {total_reposts}
Total Replies: {total_replies}
"""
    return report

def send_email(body):
    email_from = os.getenv("EMAIL_FROM")
    email_to = os.getenv("EMAIL_TO")
    email_host = os.getenv("EMAIL_HOST")
    email_port = int(os.getenv("EMAIL_PORT", 587))
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    msg = MIMEText(body)
    msg["Subject"] = "AverisAxiom Daily Report"
    msg["From"] = email_from
    msg["To"] = email_to

    with smtplib.SMTP(email_host, email_port) as server:
        server.starttls()
        server.login(email_user, email_pass)
        server.send_message(msg)

if __name__ == "__main__":
    print("Generating daily report...")
    report = generate_report()
    print(report)
    send_email(report)
    print("Report sent!")
