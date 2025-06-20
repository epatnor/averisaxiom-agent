# === File: daily_report.py ===
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def update_stats():
    print("Updating stats from database...")
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(like_count), SUM(repost_count), SUM(reply_count) FROM posts WHERE status = 'published'")
    total_published, total_likes, total_reposts, total_replies = c.fetchone()
    conn.close()
    total_likes = total_likes or 0
    total_reposts = total_reposts or 0
    total_replies = total_replies or 0
    print(f"Stats fetched: Published={total_published}, Likes={total_likes}, Reposts={total_reposts}, Replies={total_replies}")
    return total_published, total_likes, total_reposts, total_replies

def generate_report():
    total_published, total_likes, total_reposts, total_replies = update_stats()
    report = (
        f"AverisAxiom Daily Report\n\n"
        f"Total Published Posts: {total_published}\n"
        f"Total Likes: {total_likes}\n"
        f"Total Reposts: {total_reposts}\n"
        f"Total Replies: {total_replies}\n"
    )
    return report

def send_email(report):
    email_from = os.getenv("EMAIL_FROM")
    email_to = os.getenv("EMAIL_TO")
    email_host = os.getenv("EMAIL_HOST")
    email_port = int(os.getenv("EMAIL_PORT"))
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = "AverisAxiom Daily Report"

    msg.attach(MIMEText(report, 'plain'))

    try:
        print("Connecting to SMTP server...")
        server = smtplib.SMTP(email_host, email_port)
        server.starttls()
        server.login(email_user, email_pass)
        server.sendmail(email_from, email_to, msg.as_string())
        server.quit()
        print("Email successfully sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    print("Generating daily report...")
    report = generate_report()
    print("Report generated:\n")
    print(report)
    send_email(report)
