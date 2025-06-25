# === File: db.py ===

import sqlite3
import os
import json

DB_FILE = "posts.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        status TEXT,
        type TEXT,
        metrics TEXT
    )
    """)
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        base_prompt TEXT,
        style TEXT,
        model TEXT,
        temperature REAL
    )
    """)
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS scraped_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        type TEXT,
        source TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def insert_draft(draft):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO posts (title, status, type, metrics)
        VALUES (?, ?, ?, ?)
    """, (draft['title'], draft['status'], draft['type'], json.dumps(draft.get('metrics'))))
    conn.commit()
    conn.close()

def insert_scraped_item(item):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO scraped_items (title, type, source)
        VALUES (?, ?, ?)
    """, (item['title'], item['type'], item['source']))
    conn.commit()
    conn.close()

def get_pipeline():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, title, status, type, metrics FROM posts ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    
    pipeline = []
    for row in rows:
        metrics = json.loads(row[4]) if row[4] else None
        pipeline.append({
            "id": row[0],
            "title": row[1],
            "status": row[2],
            "type": row[3],
            "metrics": metrics
        })
    return pipeline

def get_settings():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT base_prompt, style, model, temperature FROM settings WHERE id = 1")
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "base_prompt": row[0],
            "style": row[1],
            "model": row[2],
            "temperature": row[3]
        }
    else:
        return {
            "base_prompt": "",
            "style": "News",
            "model": "OpenAI GPT",
            "temperature": 0.7
        }

def save_settings(settings):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO settings (id, base_prompt, style, model, temperature)
        VALUES (1, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            base_prompt=excluded.base_prompt,
            style=excluded.style,
            model=excluded.model,
            temperature=excluded.temperature
    """, (settings['base_prompt'], settings['style'], settings['model'], settings['temperature']))
    conn.commit()
    conn.close()

def get_account_stats():
    # Dummy stats
    return {
        "X (Twitter)": {"followers": 15200, "posts": 314},
        "Bluesky": {"followers": 3800, "posts": 95},
        "Mastodon": {"followers": 0, "posts": 0}
    }
