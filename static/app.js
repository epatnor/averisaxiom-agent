// app.js

const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    loadPipeline();
    loadStats();
});

function loadPipeline() {
    fetch(`${API_URL}/pipeline`)
        .then(res => res.json())
        .then(data => renderPipeline(data.concat(dummyPosts())))
        .catch(() => renderPipeline(dummyPosts()));  // fallback om API inte svarar
}

function dummyPosts() {
    return [
        { id: 1, title: "BREAKING: US strikes Iranian nuclear facility...", status: "new", type: "auto", metrics: null },
        { id: 2, title: "EU unveils ambitious green energy plan...", status: "new", type: "auto", metrics: null },
        { id: 3, title: "How will oil markets react to Iran strike?", status: "draft", type: "semi", metrics: null },
        { id: 4, title: "Tesla announces breakthrough...", status: "draft", type: "semi", metrics: null },
        { id: 5, title: "AI Conference 2025 creative preview...", status: "pending", type: "creative", metrics: null },
        { id: 6, title: "Global leaders debate carbon tax...", status: "pending", type: "creative", metrics: null },
        { id: 7, title: "US strikes Iran's nuclear facility fully confirmed...", status: "published", type: "auto", metrics: { comments: 245, likes: 3200, shares: 780 }},
        { id: 8, title: "NASA's Artemis mission lands crew on Moon...", status: "published", type: "auto", metrics: { comments: 312, likes: 5100, shares: 980 }}
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
    if (item.status === "new") {
        return `<button class='small-button' onclick='generateDraftFromNews(${item.id})'>Generate Draft</button>`;
    } else if (item.status === "draft") {
        return `<button class='small-button'>Publish</button>
                <button class='small-button'>Edit</button>
                <button class='small-button'>Delete</button>`;
    } else if (item.status === "pending") {
        return `<button class='small-button'>Post</button>
                <button class='small-button'>Edit</button>
                <button class='small-button'>Delete</button>`;
    } else if (item.status === "published") {
        return `<button class='small-button'>View</button><button class='small-button disabled'>Update Stats</button>`;
    } else {
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

function runAutomatic() {
    fetch(`${API_URL}/run_automatic_pipeline`, { method: "POST" })
        .then(() => loadPipeline());
}

function generateDraft() {
    const topic = document.getElementById("creative-topic").value;
    if (!topic) return alert("Enter topic first");
    fetch(`${API_URL}/generate_draft?topic=${encodeURIComponent(topic)}`, { method: "POST" })
        .then(() => loadPipeline());
}

function generateDraftFromNews(id) {
    alert("Draft generation from news not yet implemented.");
}

function loadStats() {
    // För framtiden, placeholder
}
