from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sqlite3

from db import DB_PATH
import scraper
import essence  # <-- ny!
import generator  # <-- redan existerande din gamla LLM generator

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

@app.post("/run_automatic_pipeline")
def run_automatic_pipeline():
    # Steg 1: Scrape
    google_news = scraper.get_google_news()
    youtube_videos = scraper.get_youtube_videos("world news")
    combined = google_news + youtube_videos

    # Extrahera headlines för AI clustering
    headlines = [item['title'] for item in combined]

    # Steg 2: AI clustering & summarizing
    storylines = essence.cluster_and_summarize(headlines)

    # Steg 3: Generera draft posts
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for story in storylines:
        print("Generating post for:", story['title'])
        draft = generator.generate_post(story['title'], story['summary'], style="News")

        c.execute("""
            INSERT INTO posts (title, status, type, created_at)
            VALUES (?, ?, ?, ?)
        """, (draft, "draft", "semi", datetime.utcnow().isoformat()))
    
    conn.commit()
    conn.close()

    return {"message": f"{len(storylines)} condensed storylines generated"}

@app.post("/delete")
def delete_post(post_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return {"message": "Post deleted"}

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
