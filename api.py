# === File: api.py ===

import db
import generator
import publisher
import scraper
import essence
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # För enkelhet i utveckling
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def update_settings(request: Request):
    settings = await request.json()
    db.save_settings(settings)
    return {"status": "saved"}

@app.get("/stats")
def get_stats():
    return db.get_account_stats()

@app.post("/run_automatic_pipeline")
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
