# === File: api.py ===

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sqlite3

from db import DB_PATH
import scraper
import publisher

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PostItem(BaseModel):
    id: int
    title: str
    status: str
    type: str
    metrics: Optional[dict] = None

class SettingsModel(BaseModel):
    base_prompt: str
    style: str
    model: str
    temperature: float

@app.get("/pipeline", response_model=List[PostItem])
def get_pipeline():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, status, type, comments, likes, shares FROM posts ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    pipeline = []
    for row in rows:
        metrics = None
        if row[2] == "published":
            metrics = {"comments": row[4], "likes": row[5], "shares": row[6]}
        pipeline.append({
            "id": row[0],
            "title": row[1],
            "status": row[2],
            "type": row[3],
            "metrics": metrics
        })
    return pipeline

@app.post("/generate_draft")
def generate_draft(topic: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO posts (title, status, type, created_at)
        VALUES (?, ?, ?, ?)
    """, (topic, "draft", "creative", datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return {"message": "Draft generated"}

@app.post("/publish")
def publish_post(post_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE posts SET status = 'pending' WHERE id = ?
    """, (post_id,))
    conn.commit()
    conn.close()
    return {"message": "Post moved to pending"}

@app.post("/post")
def post_pending(post_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE posts SET status = 'published', comments = ?, likes = ?, shares = ?, published_at = ?
        WHERE id = ?
    """, (123, 456, 78, datetime.utcnow().isoformat(), post_id))
    conn.commit()
    conn.close()
    return {"message": "Post published"}

@app.post("/delete")
def delete_post(post_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return {"message": "Post deleted"}

@app.post("/edit")
def edit_post(post_id: int, new_title: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE posts SET title = ? WHERE id = ?
    """, (new_title, post_id))
    conn.commit()
    conn.close()
    return {"message": "Post updated"}

@app.get("/settings", response_model=SettingsModel)
def get_settings():
    return {
        "base_prompt": "Current system prompt",
        "style": "News",
        "model": "OpenAI GPT",
        "temperature": 0.7
    }

@app.post("/settings")
def save_settings(settings: SettingsModel):
    print(f"Settings saved: {settings}")
    return {"message": "Settings saved"}

@app.get("/stats")
def get_account_stats():
    return {
        "X": {"followers": "15.2K", "posts": 314},
        "Bluesky": {"followers": "3.8K", "posts": 95},
        "Mastodon": {"followers": "--", "posts": "--"}
    }

@app.post("/run_automatic_pipeline")
def run_automatic_pipeline():
    print("==> Running automatic pipeline scraping...")

    google_news = scraper.fetch_google_news()
    print(f"Google News found {len(google_news)} items")

    youtube_videos = scraper.fetch_youtube_videos("world news")
    print(f"YouTube found {len(youtube_videos)} items")

    combined = google_news + youtube_videos
    print(f"Total items to insert: {len(combined)}")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for item in combined:
        print(f"Inserting: {item['title']}")
        c.execute("""
            INSERT INTO posts (title, status, type, created_at)
            VALUES (?, ?, ?, ?)
        """, (item['title'], "new", item['type'], datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

    return {"message": f"{len(combined)} new items injected into pipeline"}
