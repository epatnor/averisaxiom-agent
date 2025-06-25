
import sqlite3

def get_conn():
    return sqlite3.connect("posts.db")

def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS drafts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT, summary TEXT, content TEXT, style TEXT, status TEXT DEFAULT 'draft')''')
        c.execute('''CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY, value TEXT)''')
        conn.commit()

def insert_draft(draft):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO drafts (title, summary, content, style) VALUES (?, ?, ?, ?)", 
                  (draft['title'], draft['summary'], draft['content'], draft['style']))
        conn.commit()

def get_pipeline():
    with get_conn() as conn:
        c = conn.cursor()
        rows = c.execute("SELECT id, title, status, style FROM drafts").fetchall()
        return [{
            "id": row[0], "title": row[1], "status": row[2], "type": row[3], "metrics": None
        } for row in rows]

def get_settings():
    with get_conn() as conn:
        c = conn.cursor()
        rows = c.execute("SELECT key, value FROM settings").fetchall()
        return {row[0]: row[1] for row in rows}

def save_settings(settings):
    with get_conn() as conn:
        c = conn.cursor()
        for key, value in settings.items():
            c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()

def insert_scraped_item(item):
    pass  # Placeholder for now
