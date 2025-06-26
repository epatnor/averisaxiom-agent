// app.js – AverisAxiom Frontend Logic

const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    loadPipeline();
    document.getElementById("generate-draft-btn").addEventListener("click", generateCreativeDraft);
    document.getElementById("run-pipeline-btn").addEventListener("click", runAutomaticPipeline);
});

// Fetch pipeline data and render the list
function loadPipeline() {
    fetch(`${API_URL}/pipeline`)
        .then(res => res.json())
        .then(data => renderPipeline(data))
        .catch(err => console.error("Failed to load pipeline:", err));
}

// Render each post item
// Filnamn: app.js

function renderPipeline(data) {
    const list = document.getElementById("pipeline-list");
    list.innerHTML = "";

    data.forEach(item => {
        const div = document.createElement("div");
        div.className = "list-item";
        div.style.display = "grid";
        div.style.gridTemplateColumns = "100px 1fr 120px 160px 160px";
        div.style.alignItems = "center";
        div.style.gap = "10px";
        div.style.padding = "4px 10px";
        div.style.borderBottom = "1px solid #333";

        const status = (item.status || "").toLowerCase();
        const metrics = (status === "published")
            ? `💬${item.comments || 0} ❤️${formatLikes(item.likes || 0)} 🔁${item.shares || 0}`
            : "";

        const statusClass = `status-${status}`;
        const typeClass = `type-${(item.type || "default").toLowerCase()}`;
        const icon = typeIcon(item.type);
        const origin = (item.origin || "manual").toLowerCase();

        div.innerHTML = `
            <div class="origin-label">
                <span class="origin-tag ${origin}">${capitalize(origin)}</span>
            </div>
            <div class="title-snippet clickable">${item.title}</div>
            <div class="${statusClass}">${statusEmoji(item.status)} ${capitalize(item.status)}</div>
            <div class="${typeClass}">
                ${icon} ${capitalize(item.type || "Unknown")}
            </div>
            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 10px;">
                ${metrics ? `<div class="post-metrics">${metrics}</div>` : ""}
                <div class="action-buttons">${actionButtons(item)}</div>
            </div>
            <div class="post-editor" style="grid-column: 1 / -1; display: none;">
                <textarea class="post-editing" style="width: 100%; margin-top: 4px;">${item.summary || ''}</textarea>
                <div class="edit-controls" style="margin-top: 4px;">
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


// Buttons shown for each post
function actionButtons(item) {
    const status = (item.status || "").toLowerCase();
    if (status === "new") {
        return `<button class='small-button' onclick='generateDraftFromNews(${item.id})'>Generate Draft</button>`;
    } else if (status === "draft") {
        return `<button class='small-button' onclick='publishPost(${item.id})'>Publish</button>`;
    } else if (status === "pending") {
        return `<button class='small-button' onclick='publishPost(${item.id})'>Post</button>`;
    } else if (status === "published") {
        return `<button class='small-button'>View</button>`;
    }
    return ``;
}

// Call API to create draft from creative topic
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

// Publish the selected post
function publishPost(id) {
    fetch(`${API_URL}/publish/${id}`, { method: "POST" })
        .then(() => loadPipeline())
        .catch(err => console.error("Failed to publish post:", err));
}

// Update a post's summary
function updatePostSummary(id, summary) {
    fetch(`${API_URL}/update_summary`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, summary })
    }).then(() => loadPipeline());
}

// Generate a draft from a scraped news item
function generateDraftFromNews(id) {
    fetch(`${API_URL}/generate_draft_from_news/${id}`, { method: "POST" })
        .then(() => loadPipeline())
        .catch(err => console.error("Failed to generate draft from news:", err));
}

// Emoji indicators for post status
function statusEmoji(status) {
    switch (status.toLowerCase()) {
        case "new": return "🟡";
        case "draft": return "🟠";
        case "pending": return "🟣";
        case "published": return "🟢";
        default: return "⚪";
    }
}

// Emoji icons for post type
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

// Capitalize helper
function capitalize(str) {
    return str ? str.charAt(0).toUpperCase() + str.slice(1) : "";
}

// Format likes count
function formatLikes(likes) {
    return likes > 1000 ? (likes / 1000).toFixed(1) + "K" : likes;
}
