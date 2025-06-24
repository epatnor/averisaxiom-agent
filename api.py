# === File: api.py ===

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

# Tillåt CORS för utveckling (kan stramas åt sen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Utveckling: tillåt allt
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend statiskt från mappen "frontend"
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/pipeline")
def get_pipeline():
    return db.get_pipeline()

@app.post("/generate_draft")
def generate_draft(request: Request):
    data = request.json()
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
        print(f"Generating post for cluster: {story['title']}")
        draft = generator.generate_post(
            story['title'],
            story['summary'],
            style="News"
        )
        db.insert_draft(draft)

    # Lägg in källmaterialet också som "Auto"
    for item in all_items:
        db.insert_scraped_item(item)

    return {"status": "completed"}

# En enkel fallback på root, bara för test
@app.get("/api/health")
def health():
    return {"status": "ok"}

