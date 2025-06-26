const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    loadPipeline();

    document.getElementById("run-pipeline-btn").addEventListener("click", runAutomaticPipeline);

    document.getElementById("generate-draft-btn").addEventListener("click", () => {
        const topic = document.getElementById("creative-topic").value.trim();
        if (!topic) return;

        fetch(`${API_URL}/generate_draft`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title: topic })
        })
        .then(res => res.json())
        .then(() => {
            document.getElementById("creative-topic").value = "";
            loadPipeline();
        })
        .catch(err => console.error("Failed to generate draft:", err));
    });
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
            : "-";

        const statusClass = `status-${item.status}`;
        const typeClass = `type-${item.type}`;

        div.innerHTML = `
            <div class="title-snippet clickable">${item.title}</div>
            <div class="${statusClass}">${statusEmoji(item.status)} ${capitalize(item.status)}</div>
            <div class="${typeClass}">${typeIcon(item.type)} ${capitalize(item.type)}</div>
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

function typeIcon(type) {
    switch (type.toLowerCase()) {
        case "creative": return "✨";
        case "auto": return "🤖";
        case "semi": return "🧪";
        case "news": return "📰";
        default: return "";
    }
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
    alert("Draft generation from news not yet implemented.");
}

function runAutomaticPipeline() {
    fetch(`${API_URL}/run_automatic_pipeline`, { method: "POST" })
        .then(() => loadPipeline());
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

function formatLikes(likes) {
    return likes > 1000 ? (likes / 1000).toFixed(1) + "K" : likes;
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
