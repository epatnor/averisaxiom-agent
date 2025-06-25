const API_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
    loadPipeline();
    loadSettings();
    loadStats();
});

function loadPipeline() {
    fetch(`${API_URL}/pipeline`)
        .then(res => res.json())
        .then(data => renderPipeline(data.concat(dummyPosts())));
}

function dummyPosts() {
    return [
        { id: 1001, title: "AI Conference 2025 creative preview...", status: "pending", type: "creative", metrics: null },
        { id: 1002, title: "Global leaders debate carbon tax at COP30 summit...", status: "pending", type: "creative", metrics: null }
    ];
}

function renderPipeline(data) {
    const list = document.getElementById("pipeline-list");
    list.innerHTML = "";
    data.forEach(item => {
        const div = document.createElement("div");
        div.className = "list-item";
        const metrics = item.metrics 
            ? `💬${item.metrics.comments} ❤️${formatLikes(item.metrics.likes)} 🔁${item.metrics.shares}` 
            : "-";
        div.innerHTML = `
            <div class="title-snippet">${item.title}</div>
            <div class="status-${item.status}">${statusEmoji(item.status)} ${capitalize(item.status)}</div>
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
            return `<button class='small-button'>Generate Draft</button>`;
        case "draft":
            return `<button class='small-button'>Publish</button>`;
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

function formatLikes(likes) {
    return likes > 1000 ? (likes / 1000).toFixed(1) + "K" : likes;
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function generateDraft() {
    const topic = document.getElementById("creative-topic").value;
    if (!topic) return alert("Enter topic first");
    fetch(`${API_URL}/generate_draft`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ title: topic })
    }).then(() => loadPipeline());
}

function runAutomatic() {
    fetch(`${API_URL}/run_automatic_pipeline`, { method: "POST" })
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
