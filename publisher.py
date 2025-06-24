# === File: publisher.py ===

import sqlite3
from db import DB_PATH
from datetime import datetime

# === MOCKED publishing ===

def publish_to_bluesky(post_id, content):
    """
    MOCKED: Pretend to publish a post to Bluesky and update database.
    """
    print(f"[MOCK] Publishing to Bluesky: {content}")

    # --- Real code example (commented out for future real publishing) ---
    # from atproto import Client
    # from config import Config
    # client = Client()
    # client.login(Config.BLUESKY_HANDLE, Config.BLUESKY_APP_PASSWORD)
    # record = client.send_post(content)
    # uri = record.uri
    # ---------------------------------------------------------------

    # Simulate response for test
    uri = f"mock://bluesky/post/{post_id}"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE posts SET status = 'published', bluesky_uri = ?, published_at = ?, word_count = ? WHERE id = ?
    """, (uri, datetime.utcnow().isoformat(), len(content.split()), post_id))
    conn.commit()
    conn.close()


def update_account_stats():
    """
    MOCKED: Pretend to fetch current account stats from Bluesky.
    """
    print("[MOCK] Updating account stats from Bluesky")

    # --- Real code example (commented out for future real publishing) ---
    # from atproto import Client
    # from config import Config
    # client = Client()
    # client.login(Config.BLUESKY_HANDLE, Config.BLUESKY_APP_PASSWORD)
    # profile = client.get_profile(Config.BLUESKY_HANDLE)
    # followers = getattr(profile, "followers_count", 0)
    # following = getattr(profile, "follows_count", 0)
    # posts = getattr(profile, "posts_count", 0)
    # ---------------------------------------------------------------

    # Simulate data for now
    followers = 1234
    following = 56
    posts = 789

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO account_stats (timestamp, followers, following, posts, likes)
        VALUES (?, ?, ?, ?, ?)
    """, (datetime.utcnow().isoformat(), followers, following, posts, 0))
    conn.commit()
    conn.close()
