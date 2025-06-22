# === File: publisher.py ===

from atproto import Client
from config import Config
import sqlite3
from db import DB_PATH
from datetime import datetime

def update_account_stats():
    client = Client()
    client.login(Config.BLUESKY_HANDLE, Config.BLUESKY_APP_PASSWORD)

    profile = client.get_profile(Config.BLUESKY_HANDLE)
    followers = getattr(profile, "followers_count", 0)
    following = getattr(profile, "follows_count", 0)
    posts = getattr(profile, "posts_count", 0)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO account_stats (timestamp, followers, following, posts, likes)
        VALUES (?, ?, ?, ?, ?)
    """, (datetime.utcnow().isoformat(), followers, following, posts, 0))  # likes = 0 (för framtida användning)
    conn.commit()
    conn.close()
