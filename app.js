// app.js

const API_URL = "http://localhost:8000"; // Anpassa om du kör på annan port

document.addEventListener("DOMContentLoaded", () => {
    loadPipeline();
    loadSettings();
    loadStats();
});

function loadPipeline() {
    fetch(`${API_URL}/pipeline`)
        .then(res => res.json())
        .then(data => renderPipeline(data));
}

function renderPipeline(data) {
    const list = document.getElementById("pipeline-list");
    list.innerHTML = "";
    data.forEach(item => {
        const div = document.createElement("div");
        div.className = "list-item";

        const metrics = item.metrics 
            ? `💬${item.metrics.comments} ❤️${item.metrics.likes} 🔁${item.metrics.shares}` 
            : "-";

        div.innerHTML = `
            <div class="title-snippet">${item.title}</div>
            <div class="status-${item.status}"> ${statusEmoji(item.status)} ${capitalize(item.status)} </div>
            <div class="source">${item.source || "-"}</div>
            <div class="type-${item.type}">${capitalize(item.type)}</div>
            <div class="metrics">${metrics}</div>
            <div class="action-buttons">${actionButtons(item)}</div>
        `;
        list.appendChild(div);
    });
}


function actionButtons(item) {
    switch(item.status) {
        case "new":
            return `<button class='small-button' onclick='generateDraftFromNews(${item.id})'>Generate Draft</button>`;
        case "draft":
            return `
                <button class='small-button' onclick='publish(${item.id})'>Publish</button>
                <button class='small-button' onclick='edit(${item.id})'>Edit</button>
                <button class='small-button' onclick='deletePost(${item.id})'>Delete</button>
            `;
        case "pending":
            return `
                <button class='small-button' onclick='post(${item.id})'>Post</button>
                <button class='small-button' onclick='edit(${item.id})'>Edit</button>
                <button class='small-button' onclick='deletePost(${item.id})'>Delete</button>
            `;
        case "published":
            return `<button class='small-button'>View</button>`;
        default:
            return "";
    }
}

function statusEmoji(status) {
    switch(status) {
        case "new": return "🟡";
        case "draft": return "🟠";
        case "pending": return "🟣";
        case "published": return "🟢";
        default: return "";
    }
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function generateDraft() {
    const topic = document.getElementById("creative-topic").value;
    if (!topic) return alert("Enter topic first");
    fetch(`${API_URL}/generate_draft?topic=${encodeURIComponent(topic)}`, { method: "POST" })
        .then(() => loadPipeline());
}

function generateDraftFromNews(id) {
    console.log("Would generate draft from scraped news ID:", id);
    alert("Draft generation from news not implemented yet");
}

function publish(id) {
    fetch(`${API_URL}/publish?post_id=${id}`, { method: "POST" })
        .then(() => loadPipeline());
}

function post(id) {
    fetch(`${API_URL}/post?post_id=${id}`, { method: "POST" })
        .then(() => loadPipeline());
}

function deletePost(id) {
    if (!confirm("Delete this post?")) return;
    fetch(`${API_URL}/delete?post_id=${id}`, { method: "POST" })
        .then(() => loadPipeline());
}

function edit(id) {
    const newTitle = prompt("Enter new title:");
    if (!newTitle) return;
    fetch(`${API_URL}/edit?post_id=${id}&new_title=${encodeURIComponent(newTitle)}`, { method: "POST" })
        .then(() => loadPipeline());
}

function saveSettings() {
    const settings = {
        base_prompt: document.getElementById("base-prompt").value,
        style: document.getElementById("style").value,
        model: document.getElementById("model").value,
        temperature: parseFloat(document.getElementById("temperature").value)
    };
    fetch(`${API_URL}/settings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings)
    }).then(() => alert("Settings saved"));
}

function loadSettings() {
    fetch(`${API_URL}/settings`)
        .then(res => res.json())
        .then(settings => {
            document.getElementById("base-prompt").value = settings.base_prompt;
            document.getElementById("style").value = settings.style;
            document.getElementById("model").value = settings.model;
            document.getElementById("temperature").value = settings.temperature;
        });
}

function loadStats() {
    fetch(`${API_URL}/stats`)
        .then(res => res.json())
        .then(stats => {
            const container = document.getElementById("account-stats");
            container.innerHTML = "";
            Object.entries(stats).forEach(([platform, data]) => {
                const div = document.createElement("div");
                div.className = "stats-box";
                div.innerText = `${platform}: ${data.followers} Followers / ${data.posts} Posts`;
                container.appendChild(div);
            });
        });
}

function runAutomatic() {
    fetch(`${API_URL}/run_automatic_pipeline`, { method: "POST" })
        .then(res => res.json())
        .then(data => {
            console.log("Automatic scraping results:", data);
            let message = "\nGoogle News:\n";
            data.google_news.forEach(item => {
                message += `- ${item.title}\n`;
            });
            message += "\nYouTube:\n";
            data.youtube.forEach(item => {
                message += `- ${item.title}\n`;
            });
            alert(message);
        });
}
