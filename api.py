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

# Dynamisk sökväg till frontend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Mounta frontend på root "/"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

# Alla API-endpoints flyttas under /api

@app.get("/api/pipeline")
def get_pipeline():
    return db.get_pipeline()

@app.post("/api/generate_draft")
async def generate_draft(request: Request):
    data = await request.json()
    draft = generator.generate_post(
        data['title'],
        data.get('summary', ''),
        style=data.get('style', 'News')
    )
    db.insert_draft(draft)
    return {"status": "ok"}

@app.post("/api/publish/{post_id}")
def publish_post(post_id: int):
    post = db.get_post(post_id)
    publisher.publish(post)
    db.update_post_status(post_id, 'Published')
    return {"status": "published"}

@app.get("/api/settings")
def get_settings():
    return db.get_settings()

@app.post("/api/settings")
def update_settings(settings: dict):
    db.save_settings(settings)
    return {"status": "saved"}

@app.get("/api/stats")
def get_stats():
    return db.get_account_stats()

@app.post("/api/run_automatic_pipeline")
def run_automatic_pipeline():
    print("==> Starting automatic pipeline...")

    google_news = scraper.fetch_google_news()
    youtube_videos = scraper.fetch_youtube()

    print(f"Google News found {len(google_news)} items")
    print(f"YouTube found {len(youtube_videos)} items")

    all_items = google_news + youtube_videos
    print(f"Total items fetched: {len(all_items)}")

    headlines = [item['title'] for item in all_items]
    storylines = essence.cluster_and_summarize(headlines)
    print(f"Condensed into {len(storylines)} major storylines")

    for story in storylines:
        print(f"Generating post for cluster: {story['title']}")
        draft = generator.generate_post(
            story['title'],
            story['summary'],
            style="News"
        )
        db.insert_draft(draft)

    for item in all_items:
        db.insert_scraped_item(item)

    return {"status": "completed"}

@app.get("/api/health")
def health():
    return {"status": "ok"}
