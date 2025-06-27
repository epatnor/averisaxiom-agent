# db.py

import sqlite3
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

DB_PATH = "posts.db"

def init_db():
    if not os.path.exists(DB_PATH):
        print("==> Creating new database...")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                summary TEXT,
                status TEXT,
                type TEXT,
                origin TEXT,
                comments INTEGER,
                likes INTEGER,
                shares INTEGER,
                created_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE scraped (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                source TEXT,
                type TEXT
            )
        """)

        base_date = datetime(2025, 6, 1, 10, 30)
        dummy_posts = [
            {
                "title": "AI Takes Over the World",
                "summary": "A fictional look at a future where AI writes all the news.",
                "status": "Published",
                "type": "Satire",
                "origin": "auto",
                "comments": 12,
                "likes": 1045,
                "shares": 98,
                "created_at": (base_date + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
            },
            {
                "title": "Cats Take Over the Internet (Again)",
                "summary": "In a shocking turn of events, 90% of global content is now memes featuring cats wearing sunglasses. Resistance is futile.",
                "status": "Published",
                "type": "News",
                "origin": "auto",
                "comments": 53,
                "likes": 8792,
                "shares": 421,
                "created_at": (base_date + timedelta(days=2, hours=3)).strftime("%Y-%m-%d %H:%M")
            },
            {
                "title": "Welcome to AverisAxiom",
                "summary": "This is a test post to demonstrate layout and formatting.",
                "status": "Published",
                "type": "Creative",
                "origin": "manual",
                "comments": 5,
                "likes": 212,
                "shares": 13,
                "created_at": (base_date + timedelta(days=4, hours=1)).strftime("%Y-%m-%d %H:%M")
            }
        ]

        for post in dummy_posts:
            c.execute("""
                INSERT INTO posts (title, summary, status, type, origin, comments, likes, shares, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post["title"],
                post["summary"],
                post["status"],
                post["type"],
                post["origin"],
                post["comments"],
                post["likes"],
                post["shares"],
                post["created_at"]
            ))

        conn.commit()
        conn.close()

def insert_draft(draft):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO posts (title, summary, status, type, origin, comments, likes, shares, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        draft.get('title'),
        draft.get('summary'),
        draft.get('status'),
        draft.get('type'),
        draft.get('origin', 'manual'),
        0, 0, 0,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()
    conn.close()

def get_pipeline():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, title, summary, status, type, origin, comments, likes, shares, created_at
        FROM posts
        ORDER BY datetime(created_at) DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "title": row[1],
            "summary": row[2],
            "status": row[3],
            "type": row[4],
            "origin": row[5],
            "comments": row[6],
            "likes": row[7],
            "shares": row[8],
            "created_at": row[9]
        } for row in rows
    ]

def insert_scraped_item(item):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO scraped (title, source, type)
        VALUES (?, ?, ?)
    """, (item['title'], item['source'], item['type']))
    conn.commit()
    conn.close()

def update_post_summary(post_id, new_summary):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE posts
        SET summary = ?
        WHERE id = ?
    """, (new_summary, post_id))
    conn.commit()
    conn.close()

def update_post_origin(post_id, new_origin):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE posts
        SET origin = ?
        WHERE id = ?
    """, (new_origin, post_id))
    conn.commit()
    conn.close()

# === SETTINGS ===

def get_settings():
    load_dotenv()
    return {
        "MAX_NEWS_AGE_DAYS": os.getenv("MAX_NEWS_AGE_DAYS", "3"),
        "MAX_NEWS_ITEMS": os.getenv("MAX_NEWS_ITEMS", "25"),
        "NEWS_TOPICS": os.getenv("NEWS_TOPICS", "technology, ai, politics"),
        "ONLY_WITH_PUBDATE": os.getenv("ONLY_WITH_PUBDATE", "true")
    }

def save_settings(settings: dict):
    env_path = ".env"
    existing = {}

    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    existing[key] = val

    for key, val in settings.items():
        existing[key] = str(val)

    with open(env_path, "w") as f:
        for key, val in existing.items():
            f.write(f"{key}={val}\n")

