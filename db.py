
import sqlite3
import os

DB_PATH = "posts.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        summary TEXT,
        status TEXT,
        type TEXT,
        source TEXT,
        comments INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        shares INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()

def insert_scraped_item(item):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO posts (title, status, type, source) VALUES (?, 'new', ?, ?)", 
              (item['title'], item['type'], item['source']))
    conn.commit()
    conn.close()

def insert_draft(draft):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO posts (title, summary, status, type) VALUES (?, ?, 'draft', 'semi')",
              (draft['title'], draft['content']))
    conn.commit()
    conn.close()

def get_pipeline():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, title, summary, status, type, comments, likes, shares FROM posts ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    posts = []
    for row in rows:
        metrics = None
        if row[5] or row[6] or row[7]:
            metrics = {"comments": row[5], "likes": row[6], "shares": row[7]}
        posts.append({
            "id": row[0],
            "title": row[1],
            "summary": row[2],
            "status": row[3],
            "type": row[4],
            "metrics": metrics
        })
    return posts

def get_post(post_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT title, summary FROM posts WHERE id=?", (post_id,))
    row = c.fetchone()
    conn.close()
    return {"title": row[0], "summary": row[1]}

def update_post_status(post_id, status):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE posts SET status=? WHERE id=?", (status, post_id))
    conn.commit()
    conn.close()
