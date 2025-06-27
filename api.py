# api.py
# ✅ Main FastAPI app for AverisAxiom. Serves frontend, API endpoints, and now includes modular settings support.

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

from settings_api import router as settings_router  # 🧩 new modular settings API

# 🔧 Init DB on startup if needed
db.init_db()

# 🌐 Create FastAPI app
app = FastAPI()

# 🧩 Enable CORS (optional: limit in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📁 Mount static frontend files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 🔌 Mount new settings API
app.include_router(settings_router)

# 🌍 Serve index.html on root
@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# ⚙️ Serve settings.html at /pipeline
@app.get("/pipeline")
async def serve_settings_page():
    return FileResponse(os.path.join(STATIC_DIR, "settings.html"), media_type="text/html")

# ✍️ Manual post entry
@app.post("/insert_manual_post")
async def insert_manual_post(request: Request):
    data = await request.json()
    draft = {
        "title": data.get("title", "Untitled"),
        "summary": data.get("summary", ""),
        "status": "Draft",
        "type": "Creative",
        "origin": "manual"  # 🖋️ Manual origin marker
    }
    db.insert_draft(draft)
    return {"status": "ok"}

# 🤖 Generate AI-assisted post
@app.post("/generate_draft")
async def generate_draft(request: Request):
    data = await request.json()
    draft = generator.generate_post(
        data['topic'],
        data.get('summary', ''),
        style=data.get('style', 'Creative')
    )
    draft['origin'] = 'semi'
    db.insert_draft(draft)
    return {"status": "ok"}

# 🚀 Publish post
@app.post("/publish/{post_id}")
def publish_post(post_id: int):
    post = db.get_post(post_id)
    publisher.publish(post)
    db.update_post_status(post_id, 'Published')
    return {"status": "published"}

# 🧪 Test scraper with user settings
@app.post("/test_scraper")
async def test_scraper(request: Request):
    data = await request.json()
    result = scraper.test_google_news(data)
    return {"result": result[:3]}  # Just first 3

# 🧪 Test YouTube fetch
@app.post("/test_youtube")
async def test_youtube(request: Request):
    data = await request.json()
    result = scraper.test_youtube(data)
    return {"result": result[:3]}

# 📊 Dummy account stats
@app.get("/stats")
def get_stats():
    return db.get_account_stats()

# 🔁 Automatic pipeline (Google News + YouTube + essence)
@app.post("/run_automatic_pipeline")
def run_automatic_pipeline():
    print("==> Starting automatic pipeline...")
    google_news = scraper.fetch_google_news()
    youtube_videos = scraper.fetch_youtube_videos()
    all_items = google_news + youtube_videos

    items = [{"title": item["title"], "summary": item.get("summary", "")} for item in all_items]
    storylines = essence.generate_clustered_storylines(items)

    for story in storylines:
        draft = generator.generate_post(story['title'], story['summary'], style="News")
        draft['origin'] = 'auto'
        db.insert_draft(draft)

    return {"status": "completed"}

# 📝 Update post summary
@app.post("/update_summary")
async def update_summary(request: Request):
    data = await request.json()
    post_id = data.get("id")
    new_summary = data.get("summary")
    if not post_id or new_summary is None:
        return JSONResponse(status_code=400, content={"error": "Missing id or summary"})
    db.update_post_summary(post_id, new_summary)
    return {"status": "updated"}
