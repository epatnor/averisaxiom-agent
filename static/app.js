// app.js

const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("run-pipeline-btn").addEventListener("click", runAutomaticPipeline);
    document.getElementById("generate-draft-btn").addEventListener("click", generateCreativeDraft);
    loadPipeline();
});

function loadPipeline() {
    fetch(`${API_URL}/pipeline`)
        .then(res => res.json())
        .then(data => renderPipeline(data))
        .catch(err => console.error("Failed to load pipeline:", err));
}

function renderPipeline(data) {
    const list = document.getElementById("pipeline-list");
    list.innerHTML = "";  // Rensar listan

    data.forEach(item => {
        const row = document.createElement("div");
        row.className = "list-item";

        const metrics = (item.comments !== null)
            ? `💬${item.comments} ❤️${formatLikes(item.likes)} 🔁${item.shares}`
            : "-";

        row.innerHTML = `
            <div class="title-snippet">${item.title}</div>
            <div class="status ${statusClass(item.status)}">${statusEmoji(item.status)} ${capitalize(item.status)}</div>
            <div class="type-${item.type}">${capitalize(item.type)}</div>
            <div class="metrics">${metrics}</div>
            <div class="action-buttons">${generateActionButtons(item)}</div>
        `;
        list.appendChild(row);
    });
}

function statusClass(status) {
    return `status-${status}`;
}

function statusEmoji(status) {
    switch (status) {
        case "new": return "🟡";
        case "draft": return "🟠";
        case "pending": return "🟣";
        case "published": return "🟢";
        default: return "";
    }
}

function generateActionButtons(item) {
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
        return `<button class='small-button'>View</button>
                <button class='small-button disabled'>Update Stats</button>`;
    } else {
        return "";
    }
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatLikes(likes) {
    return (likes > 1000) ? (likes / 1000).toFixed(1) + "K" : likes;
}

function runAutomaticPipeline() {
    console.log("Running Automatic Pipeline...");
    fetch(`${API_URL}/run_automatic_pipeline`, { method: "POST" })
        .then(() => loadPipeline())
        .catch(err => console.error("Pipeline failed:", err));
}

function generateCreativeDraft() {
    const topic = document.getElementById("creative-topic").value.trim();
    if (!topic) {
        alert("Please enter a topic first");
        return;
    }

    fetch(`${API_URL}/generate_draft`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: topic })
    })
    .then(() => loadPipeline())
    .catch(err => console.error("Draft generation failed:", err));
}

function generateDraftFromNews(id) {
    alert("Not yet implemented: Generate draft from scraped news item " + id);
}
