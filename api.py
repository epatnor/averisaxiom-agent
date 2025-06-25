# === File: api.py ===

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import db
import scraper

# Init DB at startup
db.init_db()

app = FastAPI()

# CORS (öppet för utveckling)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statisk frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/pipeline")
def get_pipeline():
    return db.get_pipeline()

@app.post("/settings")
async def update_settings(request: Request):
    data = await request.json()
    db.save_settings(data)
    return {"status": "saved"}

@app.get("/settings")
def get_settings():
    return db.get_settings()

@app.get("/stats")
def get_stats():
    return db.get_account_stats()

@app.post("/run_automatic_pipeline")
def run_pipeline():
    google_news = scraper.fetch_google_news()
    youtube = scraper.fetch_youtube_videos()
    all_items = google_news + youtube

    for item in all_items:
        db.insert_scraped_item(item)
        db.insert_draft({
            "title": item['title'],
            "status": "new",
            "type": item['type'],
            "metrics": None
        })
    return {"status": "pipeline completed"}
