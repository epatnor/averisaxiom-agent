# === File: db.py ===
import sqlite3
from config import Config
import os

DB_PATH = Config.DB_PATH

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Tabell för inlägg i kö (pending) och publicerade (published)
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            post TEXT,
            status TEXT,
            bluesky_uri TEXT,
            like_count INTEGER DEFAULT 0,
            repost_count INTEGER DEFAULT 0,
            reply_count INTEGER DEFAULT 0
        )
    """)
    # Ny tabell för publicerade inlägg med publiceringsdatum
    c.execute("""
        CREATE TABLE IF NOT EXISTS published_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER UNIQUE,
            published_at TEXT,
            FOREIGN KEY(post_id) REFERENCES posts(id)
        )
    """)
    # Inställningar
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_post(prompt, post):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO posts (prompt, post, status) VALUES (?, ?, 'pending')", (prompt, post))
    conn.commit()
    conn.close()

def get_pending_posts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, prompt, post FROM posts WHERE status = 'pending' ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_published_posts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT p.id, p.prompt, p.post, p.like_count, p.repost_count, p.reply_count, pub.published_at 
        FROM posts p
        JOIN published_posts pub ON p.id = pub.post_id
        ORDER BY pub.published_at DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def publish_post(post_id):
    import datetime
    published_at = datetime.datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Markera posten som publicerad i posts-tabellen
    c.execute("UPDATE posts SET status = 'published' WHERE id = ?", (post_id,))
    # Lägg till i published_posts-tabellen med datum
    c.execute("INSERT OR IGNORE INTO published_posts (post_id, published_at) VALUES (?, ?)", (post_id, published_at))
    conn.commit()
    conn.close()

def delete_post(post_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Ta bort posten från posts och published_posts (ifall publicerad)
    c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    c.execute("DELETE FROM published_posts WHERE post_id = ?", (post_id,))
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
