# api.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Anta att vi har en databasmodul vi redan har (db.py, generator.py osv)
import db
import generator
import publisher

app = FastAPI()

# För CORS så vi kan köra frontend separat
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== MODELLER =====

class PostItem(BaseModel):
    id: int
    title: str
    status: str
    type: str
    metrics: Optional[dict]

class SettingsModel(BaseModel):
    base_prompt: str
    style: str
    model: str
    temperature: float

# ===== MOCKDATA FÖR NU =====

pipeline_mock = [
    {"id": 1, "title": "US strikes Iranian nuclear facility", "status": "new", "type": "auto", "metrics": None},
    {"id": 2, "title": "EU unveils green energy plan", "status": "new", "type": "auto", "metrics": None},
    {"id": 3, "title": "How will oil markets react", "status": "draft", "type": "semi", "metrics": None},
    {"id": 4, "title": "Tesla breakthrough in solid-state battery", "status": "draft", "type": "semi", "metrics": None},
    {"id": 5, "title": "AI Conference creative preview", "status": "pending", "type": "creative", "metrics": None},
    {"id": 6, "title": "Global leaders debate carbon tax", "status": "pending", "type": "creative", "metrics": None},
    {"id": 7, "title": "US confirms full Iran strike", "status": "published", "type": "auto", "metrics": {"comments": 245, "likes": 3200, "shares": 780}},
    {"id": 8, "title": "NASA Artemis crew lands on Moon", "status": "published", "type": "auto", "metrics": {"comments": 312, "likes": 5100, "shares": 980}}
]

settings_mock = {
    "base_prompt": "Current system prompt",
    "style": "News",
    "model": "OpenAI GPT",
    "temperature": 0.7
}

accounts_mock = {
    "X": {"followers": "15.2K", "posts": 314},
    "Bluesky": {"followers": "3.8K", "posts": 95},
    "Mastodon": {"followers": "--", "posts": "--"}
}

# ===== API ENDPOINTS =====

@app.get("/pipeline", response_model=List[PostItem])
def get_pipeline():
    return pipeline_mock

@app.post("/generate_draft")
def generate_draft(topic: str):
    print(f"Generating draft for: {topic}")
    return {"message": "Draft generated"}

@app.post("/publish")
def publish_post(post_id: int):
    print(f"Publishing post ID: {post_id}")
    return {"message": "Post published"}

@app.post("/post")
def post_pending(post_id: int):
    print(f"Posting pending ID: {post_id}")
    return {"message": "Post sent"}

@app.post("/delete")
def delete_post(post_id: int):
    print(f"Deleting post ID: {post_id}")
    return {"message": "Post deleted"}

@app.post("/edit")
def edit_post(post_id: int, new_title: str):
    print(f"Editing post ID: {post_id} to '{new_title}'")
    return {"message": "Post updated"}

@app.get("/settings", response_model=SettingsModel)
def get_settings():
    return settings_mock

@app.post("/settings")
def save_settings(settings: SettingsModel):
    print(f"Saving new settings: {settings}")
    return {"message": "Settings saved"}

@app.get("/stats")
def get_account_stats():
    return accounts_mock
