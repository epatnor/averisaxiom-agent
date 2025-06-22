# === File: db.py ===

import sqlite3
from config import Config
import os

DB_PATH = Config.DB_PATH

def init_db():
    """
    Fully robust DB initializer: 
    - If DB file missing: create full DB from scratch.
    - If DB file exists but posts table missing or incomplete: recreate DB from scratch.
    """
    if not os.path.exists(DB_PATH):
        print("Database file missing. Creating new database...")
        recreate_db()
    else:
        # Check if posts table exists and has expected columns
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("SELECT mood FROM posts LIMIT 1")
        except sqlite3.OperationalError:
            print("Existing DB is incomplete. Recreating database...")
            conn.close()
            os.remove(DB_PATH)
            recreate_db()
            return
        conn.close()

def recreate_db():
    """
    Actually creates the full DB schema.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Posts table
    c.execute("""
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            post TEXT,
            status TEXT,
            mood TEXT,
            bluesky_uri TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            published_at TEXT,
            word_count INTEGER DEFAULT 0,
            auto_mood_confidence REAL DEFAULT 0.0,
            notes TEXT,
            like_count INTEGER DEFAULT 0,
            repost_count INTEGER DEFAULT 0,
            reply_count INTEGER DEFAULT 0
        )
    """)

    # Settings table
    c.execute("""
        CREATE TABLE settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Account stats table
    c.execute("""
        CREATE TABLE account_stats (
            timestamp TEXT PRIMARY KEY,
            followers INTEGER,
            following INTEGER,
            posts INTEGER,
            likes INTEGER
        )
    """)

    conn.commit()
    conn.close()
    print("Database fully initialized.")

def save_post(prompt, post, mood):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO posts (prompt, post, status, mood, created_at, word_count)
        VALUES (?, ?, 'pending', ?, datetime('now'), ?)
    """, (prompt, post, mood, len(post.split())))
    conn.commit()
    conn.close()

def get_pending_posts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, prompt, post FROM posts WHERE status = 'pending'")
    rows = c.fetchall()
    conn.close()
    return rows

def get_published_posts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, prompt, post, bluesky_uri, mood, created_at, published_at, like_count, repost_count, reply_count
        FROM posts
        WHERE status = 'published'
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def mark_as_published(post_id, bluesky_uri):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE posts
        SET status = 'published', bluesky_uri = ?, published_at = datetime('now')
        WHERE id = ?
    """, (bluesky_uri, post_id))
    conn.commit()
    conn.close()

def delete_post(post_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE posts SET status = 'deleted' WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def get_setting(key, default=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
