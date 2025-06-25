import os
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import db
import generator
import publisher
import scraper
import essence

print("==> Starting AverisAxiom Backend with full debug logging...")

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("CORS middleware initialized.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"Base directory detected: {BASE_DIR}")

# Serve static frontend
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")
print("Static files mounted at /static")

@app.get("/")
async def serve_index():
    print("Serving index.html")
    try:
        return FileResponse(os.path.join(BASE_DIR, "index.html"))
    except Exception as e:
        print("Error serving index.html:", e)
        traceback.print_exc()
        return JSONResponse(content={"error": "Failed to serve index.html"}, status_code=500)

@app.get("/pipeline")
def get_pipeline():
    print("Fetching pipeline data...")
    try:
        pipeline = db.get_pipeline()
        print(f"Pipeline fetched: {len(pipeline)} items")
        return pipeline
    except Exception as e:
        print("Error fetching pipeline:", e)
        traceback.print_exc()
        return []

@app.post("/generate_draft")
async def generate_draft(request: Request):
    print("Incoming request: generate_draft()")
    try:
        data = await request.json()
        print("Received data:", data)
        draft = generator.generate_post(
            data['title'],
            data.get('summary', ''),
            style=data.get('style', 'News')
        )
        db.insert_draft(draft)
        print("Draft generated and inserted.")
        return {"status": "ok"}
    except Exception as e:
        print("Error in generate_draft:", e)
        traceback.print_exc()
        return JSONResponse(content={"error": "Draft generation failed"}, status_code=500)

@app.post("/publish/{post_id}")
def publish_post(post_id: int):
    print(f"Publishing post id: {post_id}")
    try:
        post = db.get_post(post_id)
        publisher.publish(post)
        db.update_post_status(post_id, 'Published')
        print("Post published successfully.")
        return {"status": "published"}
    except Exception as e:
        print("Error publishing post:", e)
        traceback.print_exc()
        return JSONResponse(content={"error": "Publish failed"}, status_code=500)

@app.get("/settings")
def get_settings():
    print("Loading settings...")
    try:
        settings = db.get_settings()
        print("Settings loaded:", settings)
        return settings
    except Exception as e:
        print("Error loading settings:", e)
        traceback.print_exc()
        return {}

@app.post("/settings")
def update_settings(settings: dict):
    print("Saving settings:", settings)
    try:
        db.save_settings(settings)
        print("Settings saved.")
        return {"status": "saved"}
    except Exception as e:
        print("Error saving settings:", e)
        traceback.print_exc()
        return JSONResponse(content={"error": "Save failed"}, status_code=500)

@app.get("/stats")
def get_stats():
    print("Fetching account stats...")
    try:
        stats = db.get_account_stats()
        print("Stats fetched:", stats)
        return stats
    except Exception as e:
        print("Error fetching stats:", e)
        traceback.print_exc()
        return {}

@app.post("/run_automatic_pipeline")
def run_automatic_pipeline():
    print("==> Starting automatic pipeline...")
    try:
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
            print(f"Generating post for: {story['title']}")
            draft = generator.generate_post(
                story['title'],
                story['summary'],
                style="News"
            )
            db.insert_draft(draft)

        for item in all_items:
            db.insert_scraped_item(item)

        print("Automatic pipeline completed.")
        return {"status": "completed"}

    except Exception as e:
        print("Error in pipeline:", e)
        traceback.print_exc()
        return JSONResponse(content={"error": "Pipeline failed"}, status_code=500)

@app.get("/api/health")
def health():
    print("Health check OK.")
    return {"status": "ok"}
