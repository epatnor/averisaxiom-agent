from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
import db
import generator
import publisher
import scraper
import essence

# Initiera FastAPI
app = FastAPI()

# CORS för frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statiska filer från ./static/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Serve index.html på root
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# API endpoints

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
    all_items = google_news + youtube_videos
    headlines = [item['title'] for item in all_items]
    storylines = essence.cluster_and_summarize(headlines)
    for story in storylines:
        draft = generator.generate_post(story['title'], story['summary'], style="News")
        db.insert_draft(draft)
    for item in all_items:
        db.insert_scraped_item(item)
    return {"status": "completed"}

@app.get("/health")
def health():
    return {"status": "ok"}
