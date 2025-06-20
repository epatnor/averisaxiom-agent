# === File: db.py ===
import sqlite3

def init_db():
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            post TEXT,
            status TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_post(prompt, post):
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("INSERT INTO posts (prompt, post, status) VALUES (?, ?, ?)", (prompt, post, "pending"))
    conn.commit()
    conn.close()

def get_pending_posts():
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("SELECT id, prompt, post FROM posts WHERE status = 'pending'")
    rows = c.fetchall()
    conn.close()
    return rows

def mark_as_published(post_id):
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("UPDATE posts SET status = 'published' WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def get_setting(key, default_value=None):
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default_value

def set_setting(key, value):
    conn = sqlite3.connect("posts.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
