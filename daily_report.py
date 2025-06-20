# === File: daily_report.py ===
import sqlite3
from atproto import Client
from config import Config
import smtplib
from email.mime.text import MIMEText

def update_stats():
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("SELECT id, bluesky_uri FROM posts WHERE status = 'published' AND bluesky_uri IS NOT NULL")
    rows = c.fetchall()
    conn.close()

    client = Client()
    client.login(Config.BLUESKY_HANDLE, Config.BLUESKY_APP_PASSWORD)

    for post_id, uri in rows:
        try:
            post = client.get_post(uri)
            like_count = post.record.like_count if hasattr(post.record, 'like_count') else 0
            repost_count = post.record.repost_count if hasattr(post.record, 'repost_count') else 0
            reply_count = post.record.reply_count if hasattr(post.record, 'reply_count') else 0

            conn = sqlite3.connect("posts.db")
            c = conn.cursor()
            c.execute("""
                UPDATE posts SET like_count = ?, repost_count = ?, reply_count = ? WHERE id = ?
            """, (like_count, repost_count, reply_count, post_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed to update stats for post {post_id}: {e}")

def generate_report():
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(like_count), SUM(repost_count), SUM(reply_count) FROM posts WHERE status = 'published'")
    total_published, total_likes, total_reposts, total_replies = c.fetchone()

    c.execute("""
        SELECT id, post, like_count, repost_count, reply_count FROM posts 
        WHERE status = 'published' AND (like_count >= 10 OR repost_count >= 5 OR reply_count >= 5)
        ORDER BY like_count DESC
    """)
    top_posts = c.fetchall()
    conn.close()

    report = f"AverisAxiom Daily Report:\n\n"
    report += f"Total Published: {total_published}\n"
    report += f"Total Likes: {total_likes or 0}\n"
    report += f"Total Reposts: {total_reposts or 0}\n"
    report += f"Total Replies: {total_replies or 0}\n\n"

    if top_posts:
        report += "High Performing Posts:\n"
        for post_id, content, likes, reposts, replies in top_posts:
            report += f"- Post #{post_id}: {likes} Likes, {reposts} Reposts, {replies} Replies\n"
            report += f"  Content: {content[:100]}...\n"
    else:
        report += "No exceptional posts today.\n"

    return report

def send_email(body):
    msg = MIMEText(body)
    msg["Subject"] = "AverisAxiom Daily Report"
    msg["From"] = Config.EMAIL_FROM
    msg["To"] = Config.EMAIL_TO

    with smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
        server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    update_stats()
    report = generate_report()
    send_email(report)
    print("Daily report sent!")
