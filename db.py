# === File: db.py ===

import sqlite3
import os

DB_FILE = "posts.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        summary TEXT,
        status TEXT,
        type TEXT,
        comments INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        shares INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def insert_post(title, summary, status, type_):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO posts (title, summary, status, type) VALUES (?, ?, ?, ?)", (title, summary, status, type_))
    conn.commit()
    conn.close()

def get_pipeline():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, title, summary, status, type, comments, likes, shares FROM posts ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    pipeline = []
    for row in rows:
        pipeline.append({
            "id": row[0],
            "title": row[1],
            "summary": row[2],
            "status": row[3],
            "type": row[4],
            "metrics": {
                "comments": row[5],
                "likes": row[6],
                "shares": row[7]
            }
        })
    return pipeline
