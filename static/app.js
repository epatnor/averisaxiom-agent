// app.js – Main frontend logic for AverisAxiom control panel

const API_URL = "http://localhost:8000";

// Körs när sidan laddats
document.addEventListener("DOMContentLoaded", () => {
    loadPipeline(); // Hämta och rendera poster
    document.getElementById("generate-draft-btn").addEventListener("click", generateCreativeDraft);
    document.getElementById("run-pipeline-btn").addEventListener("click", runAutomaticPipeline);
});

// Hämtar pipeline-data från backend
function loadPipeline() {
    fetch(`${API_URL}/pipeline`)
        .then(res => res.json())
        .then(data => renderPipeline(data))
        .catch(err => console.error("Failed to load pipeline:", err));
}

// Renderar pipeline-poster i listan
function renderPipeline(data) {
    const list = document.getElementById("pipeline-list");
    list.innerHTML = "";

    data.forEach(item => {
        const div = document.createElement("div");
        div.className = "list-item";
        div.style.display = "grid";
        div.style.gridTemplateColumns = "100px 1fr 120px 140px 180px";
        div.style.alignItems = "center";
        div.style.gap = "10px";
        div.style.padding = "8px 0";
        div.style.borderBottom = "1px solid #333";

        const metrics = item.metrics
            ? `💬${item.metrics.comments} ❤️${formatLikes(item.metrics.likes)} 🔁${item.metrics.shares}`
            : `💬${item.comments || 0} ❤️${formatLikes(item.likes || 0)} 🔁${item.shares || 0}`;

        const statusClass = `status-${item.status.toLowerCase()}`;
        const typeClass = `type-${(item.type || "default").toLowerCase()}`;
        const icon = typeIcon(item.type);
        const origin = capitalize(item.origin || "manual");

        div.innerHTML = `
            <div class="origin-label"><span class="origin-tag">${origin}</span></div>
            <div class="title-snippet clickable">${item.title}</div>
            <div class="${statusClass}">${statusEmoji(item.status)} ${capitalize(item.status)}</div>
            <div class="${typeClass}">${icon} ${capitalize(item.type || "Unknown")}</div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div class="post-metrics">${metrics}</div>
                <div class="action-buttons">${actionButtons(item)}</div>
            </div>
            <div class="post-editor" style="grid-column: 1 / -1; display:none;">
                <textarea class="post-editing" style="width: 100%; margin-top: 4px;">${item.summary || ''}</textarea>
                <div class="edit-controls" style="margin-top: 4px;">
                    <button class="small-button save-btn" data-id="${item.id}">Save</button>
                    <button class="small-button cancel-btn">Cancel</button>
                </div>
            </div>
        `;

        // Expandera/komprimera editor
        div.querySelector(".title-snippet").addEventListener("click", () => {
            const editor = div.querySelector(".post-editor");
            editor.style.display = editor.style.display === "none" ? "block" : "none";
        });

        // Spara redigerad summering
        div.querySelector(".save-btn").addEventListener("click", () => {
            const newSummary = div.querySelector(".post-editing").value;
            updatePostSummary(item.id, newSummary);
        });

        // Avbryt redigering
        div.querySelector(".cancel-btn").addEventListener("click", () => {
            div.querySelector(".post-editor").style.display = "none";
        });

        list.appendChild(div);
    });
}

// Returnerar knappar baserat på postens status
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
    return "";
}

// Skicka ny kreativ prompt till backend
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

// Skicka publiceringsförfrågan
function publishPost(id) {
    fetch(`${API_URL}/publish/${id}`, { method: "POST" })
        .then(() => loadPipeline())
        .catch(err => console.error("Failed to publish post:", err));
}

// Uppdatera summeringstext
function updatePostSummary(id, summary) {
    fetch(`${API_URL}/update_summary`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, summary })
    }).then(() => loadPipeline());
}

// Generera draft från nyhetsartikel
function generateDraftFromNews(id) {
    fetch(`${API_URL}/generate_draft_from_news/${id}`, { method: "POST" })
        .then(() => loadPipeline())
        .catch(err => console.error("Failed to generate draft from news:", err));
}

// Kör automatiskt flöde (feeds -> clustering -> draft generation)
function runAutomaticPipeline() {
    fetch(`${API_URL}/run_automatic_pipeline`, { method: "POST" })
        .then(() => loadPipeline());
}

// Returnerar emoji för status
function statusEmoji(status) {
    switch (status.toLowerCase()) {
        case "new": return "🟡";
        case "draft": return "🟠";
        case "pending": return "🟣";
        case "published": return "🟢";
        default: return "⚪";
    }
}

// Returnerar ikon beroende på typ
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

// Gör första bokstaven stor
function capitalize(str) {
    return str ? str.charAt(0).toUpperCase() + str.slice(1) : "";
}

// Formattera likes med K
function formatLikes(likes) {
    return likes > 1000 ? (likes / 1000).toFixed(1) + "K" : likes;
}
