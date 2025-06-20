# === File: db.py ===
import sqlite3
import os

DB_PATH = "/mnt/data/posts.db"

# Ensure database directory exists (for safety)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt TEXT,
        post TEXT,
        status TEXT,
        like_count INTEGER DEFAULT 0,
        repost_count INTEGER DEFAULT 0,
        reply_count INTEGER DEFAULT 0,
        bluesky_uri TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    conn.commit()
    conn.close()

def save_post(prompt, post):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO posts (prompt, post, status) VALUES (?, ?, ?)", (prompt, post, "pending"))
    conn.commit()
    conn.close()

def get_pending_posts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, prompt, post FROM posts WHERE status = 'pending'")
    rows = c.fetchall()
    conn.close()
    return rows

def get_setting(key, default_value=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return default_value

def set_setting(key, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
