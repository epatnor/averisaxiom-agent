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
                origin TEXT,  -- Ny kolumn
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
        conn.commit()
        conn.close()

def insert_draft(draft):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO posts (title, summary, status, type, origin, comments, likes, shares)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        draft['title'],
        draft['summary'],
        draft['status'],
        draft['type'],
        draft.get('origin', 'manual'),
        0, 0, 0
    ))
    conn.commit()
    conn.close()

def get_pipeline():
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
