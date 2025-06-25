# === File: api.py ===

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import db
import generator
import publisher
import scraper
import essence

app = FastAPI()

# CORS för utveckling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dynamiskt path till static-folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
print(f"==> Serving static files from: {STATIC_DIR}")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

# API Endpoints
@app.get("/pipeline")
def get_pipeline():
    return db.get_pipeline()

@app.post("/generate_draft")
async def generate_draft(request: Request):
    data = await request.json()
    draft = generator.generate_post(
        data['title'],
        data.get('summary', ''),
        style=data.get('style', 'News')
    )
    db.insert_draft(draft)
    return {"status": "ok"}

@app.post("/publish/{post_id}")
def publish_post(post_id: int):
    post = db.get_post(post_id)
    publisher.publish(post)
    db.update_post_status(post_id, 'Published')
    return {"status": "published"}

@app.get("/settings")
def get_settings():
    return db.get_settings()

@app.post("/settings")
def update_settings(settings: dict):
    db.save_settings(settings)
    return {"status": "saved"}

@app.get("/stats")
def get_stats():
    return db.get_account_stats()

@app.post("/run_automatic_pipeline")
def run_automatic_pipeline():
    print("==> Running automatic pipeline...")

    google_news = scraper.fetch_google_news()
    youtube_videos = scraper.fetch_youtube()

    all_items = google_news + youtube_videos
    print(f"Total items fetched: {len(all_items)}")

    headlines = [item['title'] for item in all_items]
    storylines = essence.cluster_and_summarize(headlines)
    print(f"Generated {len(storylines)} condensed storylines")

    for story in storylines:
        print(f"Generating draft for: {story['title']}")
        draft = generator.generate_post(story['title'], story['summary'], style="News")
        db.insert_draft(draft)

    for item in all_items:
        db.insert_scraped_item(item)

    return {"status": "completed"}
