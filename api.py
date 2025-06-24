# === File: api.py ===

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import db
import generator
import publisher
import scraper
import essence

# Skapa separat API-app
api = FastAPI()

# Tillåt CORS (för utveckling, kan stramas åt sen)
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === MODELLER ===
class DraftRequest(BaseModel):
    title: str
    summary: str = ""
    style: str = "News"

class SettingsModel(BaseModel):
    base_prompt: str
    style: str
    model: str
    temperature: float

# === API ENDPOINTS ===

@api.get("/pipeline")
def get_pipeline():
    return db.get_pipeline()

@api.post("/generate_draft")
def generate_draft(request: DraftRequest):
    draft = generator.generate_post(
        request.title,
        request.summary,
        style=request.style
    )
    db.insert_draft(draft)
    return {"status": "ok"}

@api.post("/publish/{post_id}")
def publish_post(post_id: int):
    post = db.get_post(post_id)
    publisher.publish(post)
    db.update_post_status(post_id, 'Published')
    return {"status": "published"}

@api.get("/settings")
def get_settings():
    return db.get_settings()

@api.post("/settings")
def update_settings(settings: SettingsModel):
    db.save_settings(settings.dict())
    return {"status": "saved"}

@api.get("/stats")
def get_stats():
    return db.get_account_stats()

@api.post("/run_automatic_pipeline")
def run_automatic_pipeline():
    print("==> Starting automatic pipeline...")

    # Hämta ny data
    google_news = scraper.fetch_google_news()
    youtube_videos = scraper.fetch_youtube()

    print(f"Google News found {len(google_news)} items")
    print(f"YouTube found {len(youtube_videos)} items")

    all_items = google_news + youtube_videos
    print(f"Total items fetched: {len(all_items)}")

    # Sammanfatta och klustra via AI
    headlines = [item['title'] for item in all_items]
    storylines = essence.cluster_and_summarize(headlines)
    print(f"Condensed into {len(storylines)} major storylines")

    # Generera utkast från storylines
    for story in storylines:
        print(f"Generating post for cluster: {story.get('title', 'N/A')}")
        draft = generator.generate_post(
            story.get('title', ''),
            story.get('summary', ''),
            style="News"
        )
        db.insert_draft(draft)

    # Lägg in källmaterialet också som "Auto"
    for item in all_items:
        db.insert_scraped_item(item)

    return {"status": "completed"}

# Hälsokontroll
@api.get("/health")
def health():
    return {"status": "ok"}

# === HUVUDAPP ===
app = FastAPI()

# Montera API på /api (snyggare separation)
app.mount("/api", api)

# Serve frontend statiskt från mappen "frontend"
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
