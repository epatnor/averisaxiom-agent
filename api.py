# api.py

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

import db
import generator
import publisher
import scraper
import essence

# Initierar databasen om den inte redan finns
db.init_db()

app = FastAPI()

# Tillåt CORS för frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kopplar statiska filer (frontend)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Root endpoint levererar frontend
@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# Returnerar innehållet i pipelinen (t.ex. drafts)
@app.get("/pipeline")
def get_pipeline():
    return db.get_pipeline()

# Skapar ett AI-assisterat utkast (semi-auto)
@app.post("/generate_draft")
async def generate_draft(request: Request):
    data = await request.json()
    story = {
        "title": data["topic"],
        "summary": data.get("summary", "")
    }
    draft = generator.generate_full_post(story)
    draft["origin"] = "semi"
    db.insert_draft(draft)
    return {"status": "ok"}

# Lägger till ett manuellt inlägg
@app.post("/insert_manual_post")
async def insert_manual_post(request: Request):
    data = await request.json()
    draft = {
        "title": data.get("title", "Untitled"),
        "summary": data.get("summary", ""),
        "status": "Draft",
        "type": "Creative",
        "origin": "manual"
    }
    db.insert_draft(draft)
    return {"status": "ok"}

# Publicerar ett inlägg till sociala medier
@app.post("/publish/{post_id}")
def publish_post(post_id: int):
    post = db.get_post(post_id)
    publisher.publish(post)
    db.update_post_status(post_id, "Published")
    return {"status": "published"}

# Hämtar inställningar från databasen
@app.get("/settings")
def get_settings():
    return db.get_settings()

# Uppdaterar inställningar
@app.post("/settings")
async def update_settings(request: Request):
    settings = await request.json()
    db.save_settings(settings)
    return {"status": "saved"}

# Returnerar kontostatistik (antal likes etc.)
@app.get("/stats")
def get_stats():
    return db.get_account_stats()

# Kör hela automatiska pipelinen
@app.post("/run_automatic_pipeline")
def run_automatic_pipeline():
    print("==> Starting automatic pipeline...")
    google_news = scraper.fetch_google_news()
    youtube_videos = scraper.fetch_youtube_videos()
    all_items = google_news + youtube_videos

    # Strukturera om till rätt format
    items = [{"title": item["title"], "summary": item.get("summary", "")} for item in all_items]
    storylines = essence.generate_clustered_storylines(items)

    for story in storylines:
        draft = generator.generate_full_post(story)
        draft["origin"] = "auto"
        db.insert_draft(draft)

    return {"status": "completed"}

# Uppdaterar sammanfattningen för ett inlägg
@app.post("/update_summary")
async def update_summary(request: Request):
    data = await request.json()
    post_id = data.get("id")
    new_summary = data.get("summary")
    if not post_id or new_summary is None:
        return JSONResponse(status_code=400, content={"error": "Missing id or summary"})
    db.update_post_summary(post_id, new_summary)
    return {"status": "updated"}
