# db.py

import sqlite3
import os

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
                shares INTEGER
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

        dummy_posts = [
            {
                "title": "AI Takes Over the World",
                "summary": "A fictional look at a future where AI writes all the news.",
                "status": "Published",
                "type": "Satire",
                "origin": "auto",
                "comments": 12,
                "likes": 1045,
                "shares": 98
            },
            {
                "title": "Cats Take Over the Internet (Again)",
                "summary": "In a shocking turn of events, 90% of global content is now memes featuring cats wearing sunglasses. Resistance is futile.",
                "status": "Published",
                "type": "News",
                "origin": "auto",
                "comments": 53,
                "likes": 8792,
                "shares": 421
            },
            {
                "title": "Welcome to AverisAxiom",
                "summary": "This is a test post to demonstrate layout and formatting.",
                "status": "Published",
                "type": "Creative",
                "origin": "manual",
                "comments": 5,
                "likes": 212,
                "shares": 13
            }
        ]

        for post in dummy_posts:
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
