// app.js

const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    loadPipeline();
    document.getElementById("generate-draft-btn").addEventListener("click", generateCreativeDraft);
    document.getElementById("run-pipeline-btn").addEventListener("click", runAutomaticPipeline);
});

// Hämta alla poster från backend
function loadPipeline() {
    fetch(`${API_URL}/pipeline`)
        .then(res => res.json())
        .then(data => renderPipeline(data))
        .catch(err => {
            console.error("Failed to load pipeline:", err);
        });
}

// Rendera listan av poster
function renderPipeline(data) {
    const list = document.getElementById("pipeline-list");
    list.innerHTML = "";

    data.forEach(item => {
        const div = document.createElement("div");
        div.className = "list-item";

        const metrics = item.metrics
            ? `💬${item.metrics.comments} ❤️${formatLikes(item.metrics.likes)} 🔁${item.metrics.shares}`
            : "-";

        const statusClass = `status-${item.status.toLowerCase()}`;
        const typeClass = `type-${(item.type || "default").toLowerCase()}`;
        const icon = typeIcon(item.type);
        const origin = typeOrigin(item.status, item.type);

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

// Actions beroende på status
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

// Skicka ny kreativ prompt
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

// Publicera post
function publishPost(id) {
    fetch(`${API_URL}/publish/${id}`, { method: "POST" })
        .then(() => loadPipeline())
        .catch(err => console.error("Failed to publish post:", err));
}

// Uppdatera summering
function updatePostSummary(id, summary) {
    fetch(`${API_URL}/update_summary`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, summary })
    }).then(() => loadPipeline());
}

// Skapa draft från nyhet
function generateDraftFromNews(id) {
    fetch(`${API_URL}/generate_draft_from_news/${id}`, { method: "POST" })
        .then(() => loadPipeline())
        .catch(err => console.error("Failed to generate draft from news:", err));
}

// Kör pipeline
function runAutomaticPipeline() {
    fetch(`${API_URL}/run_automatic_pipeline`, { method: "POST" })
        .then(() => loadPipeline());
}

// Hjälpfunktioner
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

function typeOrigin(status, type) {
    const s = (status || "").toLowerCase();
    if (s === "new") return "Auto";
    if (s === "draft" && type) return "Semi";
    if (s === "pending") return "Creative";
    if (s === "published") return "Auto";
    return "Manual";
}


function capitalize(str) {
    return str ? str.charAt(0).toUpperCase() + str.slice(1) : "";
}

function formatLikes(likes) {
    return likes > 1000 ? (likes / 1000).toFixed(1) + "K" : likes;
}
