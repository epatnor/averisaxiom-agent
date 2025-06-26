# db.py

import sqlite3
import os

DB_PATH = "posts.db"

# Dummydata som injiceras vid första skapandet av databasen
DUMMY_POSTS = [
    {
        "title": "AI beats humans at Dota 2 again",
        "summary": "An OpenAI system has once more surpassed top players in competitive gaming.",
        "status": "published",
        "type": "News",
        "origin": "auto",
        "comments": 12,
        "likes": 945,
        "shares": 102
    },
    {
        "title": "Cats officially take over the Internet",
        "summary": "Experts say it's now 90% memes, 10% actual news.",
        "status": "published",
        "type": "Joke",
        "origin": "manual",
        "comments": 3,
        "likes": 1503,
        "shares": 54
    }
]

def init_db():
    first_time = not os.path.exists(DB_PATH)
    if first_time:
        print("==> Creating new database...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            summary TEXT,
            status TEXT,
            type TEXT,
            origin TEXT,
            comments INTEGER,
            likes INTEGER,
            shares INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS scraped (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            source TEXT,
            type TEXT
        )
    """)

    if first_time:
        for post in DUMMY_POSTS:
            c.execute("""
                INSERT INTO posts (title, summary, status, type, origin, comments, likes, shares)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post["title"],
                post["summary"],
                post["status"],
                post["type"],
                post["origin"],
                post["comments"],
                post["likes"],
                post["shares"]
            ))

    conn.commit()
    conn.close()

def insert_draft(draft):
    """Lägger till ett nytt utkast i databasen"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO posts (title, summary, status, type, origin, comments, likes, shares)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        draft.get('title'),
        draft.get('summary'),
        draft.get('status'),
        draft.get('type'),
        draft.get('origin', 'manual'),
        0, 0, 0
    ))
    conn.commit()
    conn.close()

def get_pipeline():
    """Hämtar alla inlägg för pipeline-vyn"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, title, summary, status, type, origin, comments, likes, shares
        FROM posts
        ORDER BY id DESC
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
            "shares": row[8]
        } for row in rows
    ]

def insert_scraped_item(item):
    """Lägger till ett scrapat nyhetsämne"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO scraped (title, source, type)
        VALUES (?, ?, ?)
    """, (item['title'], item['source'], item['type']))
    conn.commit()
    conn.close()

def update_post_summary(post_id, new_summary):
    """Uppdaterar summeringen för ett visst inlägg"""
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
    """Uppdaterar origin-fältet (manual/auto)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE posts
        SET origin = ?
        WHERE id = ?
    """, (new_origin, post_id))
    conn.commit()
    conn.close()
