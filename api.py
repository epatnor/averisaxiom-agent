
import os
import sqlite3
import json
import requests
import feedparser
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import db
import scraper
import essence
import generator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

@app.get("/pipeline")
def get_pipeline():
    return db.get_pipeline()

@app.get("/settings")
def get_settings():
    return db.get_settings()

@app.post("/settings")
async def update_settings(request: Request):
    settings = await request.json()
    db.save_settings(settings)
    return {"status": "saved"}

@app.post("/generate_draft")
async def generate_draft(request: Request):
    data = await request.json()
    draft = generator.generate_post(data['title'], data.get('summary', ''), data.get('style', 'News'))
    db.insert_draft(draft)
    return {"status": "ok"}

@app.post("/run_automatic_pipeline")
def run_automatic_pipeline():
    google_news = scraper.fetch_google_news()
    youtube = scraper.fetch_youtube_videos()
    all_items = google_news + youtube

    headlines = [item['title'] for item in all_items]
    clusters = essence.cluster_and_summarize(headlines)

    for story in clusters:
        draft = generator.generate_post(story['title'], story['summary'], "News")
        db.insert_draft(draft)

    for item in all_items:
        db.insert_scraped_item(item)

    return {"status": "completed"}
