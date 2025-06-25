
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import db, scraper

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/")
async def serve_index():
    with open(os.path.join(BASE_DIR, "static/index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/pipeline")
def get_pipeline():
    return db.get_pipeline()

@app.post("/run_automatic_pipeline")
def run_automatic_pipeline():
    news = scraper.fetch_google_news()
    youtube = scraper.fetch_youtube_videos()
    all_items = news + youtube
    for item in all_items:
        db.insert_scraped_item(item)
    return {"inserted": len(all_items)}
