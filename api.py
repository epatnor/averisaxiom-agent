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
const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    loadPipeline();
    document.getElementById("generate-draft-btn").addEventListener("click", generateCreativeDraft);
    document.getElementById("run-pipeline-btn").addEventListener("click", runAutomaticPipeline);
});

function loadPipeline() {
    fetch(`${API_URL}/pipeline`)
        .then(res => res.json())
        .then(data => renderPipeline(data))
        .catch(err => {
            console.error("Failed to load pipeline:", err);
        });
}

function renderPipeline(data) {
    const list = document.getElementById("pipeline-list");
    list.innerHTML = "";

    data.forEach(item => {
        const div = document.createElement("div");
        div.className = "list-item";

        const metrics = item.metrics
            ? `💬${item.metrics.comments} ❤️${formatLikes(item.metrics.likes)} 🔁${item.metrics.shares}`
            : `💬${item.comments || 0} ❤️${formatLikes(item.likes || 0)} 🔁${item.shares || 0}`;

        const statusClass = `status-${item.status.toLowerCase()}`;
        const typeClass = `type-${(item.type || "default").toLowerCase()}`;
        const icon = typeIcon(item.type);
        const origin = capitalize(item.origin || "manual");

        div.innerHTML = `
            <div class="title-snippet clickable">${item.title}</div>
            <div class="${statusClass}">${statusEmoji(item.status)} ${capitalize(item.status)}</div>
            <div class="${typeClass}">
                ${icon} ${capitalize(item.type || "Unknown")}
                <span class="origin-tag">${origin}</span>
            </div>
            <div class="post-metrics">${metrics}</div>
            <div class="action-buttons">${actionButtons(item)}</div>
            <div class="post-editor" style="display:none;">
                <textarea class="post-editing">${item.summary || ''}</textarea>
                <div class="edit-controls">
                    <button class="small-button save-btn" data-id="${item.id}">Save</button>
                    <button class="small-button cancel-btn">Cancel</button>
                </div>
            </div>
        `;

        div.querySelector(".title-snippet").addEventListener("click", () => {
            const editor = div.querySelector(".post-editor");
            editor.style.display = editor.style.display === "none" ? "block" : "none";
        });

        div.querySelector(".save-btn").addEventListener("click", () => {
            const newSummary = div.querySelector(".post-editing").value;
            updatePostSummary(item.id, newSummary);
        });

        div.querySelector(".cancel-btn").addEventListener("click", () => {
            div.querySelector(".post-editor").style.display = "none";
        });

        list.appendChild(div);
    });
}

function actionButtons(item) {
    if (item.status === "new") {
        return `<button class='small-button' onclick='generateDraftFromNews(${item.id})'>Generate Draft</button>`;
    } else if (item.status === "draft") {
        return `<button class='small-button' onclick='publishPost(${item.id})'>Publish</button>`;
    } else if (item.status === "pending") {
        return `<button class='small-button' onclick='publishPost(${item.id})'>Post</button>`;
    } else if (item.status === "published") {
        return `<button class='small-button'>View</button>`;
    }
    return "";
}

function generateCreativeDraft() {
    const topic = document.getElementById("creative-topic").value;
    if (!topic) return;
    fetch(`${API_URL}/generate_draft`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic })
    }).then(() => {
        document.getElementById("creative-topic").value = "";
        loadPipeline();
    });
}

function publishPost(id) {
    fetch(`${API_URL}/publish/${id}`, { method: "POST" })
        .then(() => loadPipeline())
        .catch(err => console.error("Failed to publish post:", err));
}

function updatePostSummary(id, summary) {
    fetch(`${API_URL}/update_summary`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, summary })
    }).then(() => loadPipeline());
}

function generateDraftFromNews(id) {
    fetch(`${API_URL}/generate_draft_from_news/${id}`, { method: "POST" })
        .then(() => loadPipeline())
        .catch(err => console.error("Failed to generate draft from news:", err));
}

function runAutomaticPipeline() {
    fetch(`${API_URL}/run_automatic_pipeline`, { method: "POST" })
        .then(() => loadPipeline());
}

function statusEmoji(status) {
    switch (status.toLowerCase()) {
        case "new": return "🟡";
        case "draft": return "🟠";
        case "pending": return "🟣";
        case "published": return "🟢";
        default: return "⚪";
    }
}

function typeIcon(type) {
    switch ((type || "").toLowerCase()) {
        case "creative": return "✨";
        case "news": return "📰";
        case "thought": return "🧠";
        case "question": return "❓";
        case "satire": return "🎭";
        case "raw": return "🧵";
        case "rant": return "😡";
        case "joke": return "😂";
        default: return "📄";
    }
}

function capitalize(str) {
    return str ? str.charAt(0).toUpperCase() + str.slice(1) : "";
}

function formatLikes(likes) {
    return likes > 1000 ? (likes / 1000).toFixed(1) + "K" : likes;
}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/pipeline")
def get_pipeline():
    return db.get_pipeline()


@app.post("/generate_draft")
async def generate_draft(request: Request):
    data = await request.json()
    draft = generator.generate_post(
        data['topic'],
        data.get('summary', ''),
        style=data.get('style', 'Creative')
    )
    draft['origin'] = 'manual'
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
    youtube_videos = scraper.fetch_youtube_videos()
    all_items = google_news + youtube_videos
    headlines = [item['title'] for item in all_items]
    storylines = essence.cluster_and_summarize(headlines)
    for story in storylines:
        draft = generator.generate_post(story['title'], story['summary'], style="News")
        draft['origin'] = 'auto'
        db.insert_draft(draft)
    return {"status": "completed"}


@app.post("/update_summary")
async def update_summary(request: Request):
    data = await request.json()
    post_id = data.get("id")
    new_summary = data.get("summary")
    if not post_id or new_summary is None:
        return JSONResponse(status_code=400, content={"error": "Missing id or summary"})
    db.update_post_summary(post_id, new_summary)
    return {"status": "updated"}
