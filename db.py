import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "posts.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def setup_database():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            summary TEXT,
            type TEXT,
            status TEXT,
            metrics TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_scraped_item(item):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO posts (title, type, status) VALUES (?, ?, ?)
    """, (item['title'], item['type'], 'new'))
    conn.commit()
    conn.close()

def insert_draft(draft):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO posts (title, summary, type, status) VALUES (?, ?, ?, ?)
    """, (draft['title'], draft['summary'], draft['type'], 'draft'))
    conn.commit()
    conn.close()

def get_pipeline():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, title, summary, type, status FROM posts ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append({
            'id': row[0],
            'title': row[1],
            'summary': row[2],
            'type': row[3],
            'status': row[4],
            'metrics': None  # För enkelhet just nu
        })
    return data

def get_settings():
    # Dummy settings
    return {
        "base_prompt": "Write a short engaging post:",
        "style": "News",
        "model": "OpenAI GPT",
        "temperature": 0.7
    }

def save_settings(settings):
    pass  # Vi sparar inte settings ännu

def get_account_stats():
    # Dummy stats
    return {
        "X (Twitter)": {"followers": "15.2K", "posts": 314},
        "Bluesky": {"followers": "3.8K", "posts": 95},
        "Mastodon": {"followers": "--", "posts": 0}
    }

def get_post(post_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, title, summary, type, status FROM posts WHERE id = ?", (post_id,))
    row = c.fetchone()
    conn.close()

    if row:
        return {
            'id': row[0],
            'title': row[1],
            'summary': row[2],
            'type': row[3],
            'status': row[4]
        }
    return None

def update_post_status(post_id, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE posts SET status = ? WHERE id = ?", (status, post_id))
    conn.commit()
    conn.close()

# Kör setup vid import
setup_database()
