# === File: update_stats.py ===
from atproto import Client
from config import Config
import sqlite3

def fetch_and_update_stats():
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
            print(f"Updated stats for post {post_id}: {like_count} likes, {repost_count} reposts, {reply_count} replies")
        except Exception as e:
            print(f"Failed to update stats for post {post_id}: {e}")

if __name__ == "__main__":
    fetch_and_update_stats()
