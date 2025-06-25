
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "posts.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            type TEXT,
            source TEXT,
            status TEXT DEFAULT 'new'
        )''')
        conn.commit()

def insert_scraped_item(item):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO posts (title, type, source) VALUES (?, ?, ?)", 
                  (item['title'], item['type'], item['source']))
        conn.commit()

def get_pipeline():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, title, type, source, status FROM posts ORDER BY id DESC")
        rows = c.fetchall()
        return [{"id": r[0], "title": r[1], "type": r[2], "source": r[3], "status": r[4]} for r in rows]
