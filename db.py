# === File: db.py ===

import sqlite3
from config import Config
import os

DB_PATH = Config.DB_PATH

def init_db():
    """
    Initialize the SQLite database and create tables if they don't exist.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Posts table with status: pending, published, deleted
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            post TEXT,
            status TEXT,
            bluesky_uri TEXT,
            like_count INTEGER DEFAULT 0,
            repost_count INTEGER DEFAULT 0,
            reply_count INTEGER DEFAULT 0,
            mood TEXT DEFAULT 'news'
        )
    """)

    # Settings table for key-value pairs
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_post(prompt, post, mood="news"):
    """
    Save a new post with status 'pending' and given mood.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO posts (prompt, post, status, mood) VALUES (?, ?, 'pending', ?)", (prompt, post, mood))
    conn.commit()
    conn.close()

def get_pending_posts():
    """
    Retrieve posts with status 'pending'.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, prompt, post FROM posts WHERE status = 'pending'")
    rows = c.fetchall()
    conn.close()
    return rows

def get_published_posts():
    """
    Retrieve posts with status 'published'.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, prompt, post, bluesky_uri, like_count, repost_count, reply_count FROM posts WHERE status = 'published'")
    rows = c.fetchall()
    conn.close()
    return rows

def mark_as_published(post_id, bluesky_uri):
    """
    Update a post status to 'published' and store the Bluesky URI.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE posts SET status = 'published', bluesky_uri = ? WHERE id = ?", (bluesky_uri, post_id))
    conn.commit()
    conn.close()

def delete_post(post_id):
    """
    Mark a post as 'deleted'.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE posts SET status = 'deleted' WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def get_setting(key, default=None):
    """
    Retrieve a setting value by key.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key, value):
    """
    Insert or update a setting key-value pair.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
