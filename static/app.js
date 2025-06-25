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
    // Vi renderar listan på befintliga statiska list-element
    const rows = document.querySelectorAll(".list-item");

    rows.forEach((row, index) => {
        if (index >= data.length) {
            row.style.display = "none";  // döljer överflödiga dummy-rader
            return;
        }
        const item = data[index];
        row.querySelector(".title-snippet").textContent = item.title;
        row.querySelector(".status").textContent = getStatusText(item.status);
        row.querySelector(".status").className = `status status-${item.status}`;
        row.querySelector(".type").textContent = capitalize(item.type);
        row.querySelector(".type").className = `type-${item.type}`;

        const metrics = item.comments != null 
            ? `💬${item.comments} ❤️${formatLikes(item.likes)} 🔁${item.shares}` 
            : "-";
        row.querySelector(".metrics").textContent = metrics;

        const buttonsContainer = row.querySelector(".action-buttons");
        buttonsContainer.innerHTML = generateActionButtons(item);
    });
}

function getStatusText(status) {
    switch (status) {
        case "new": return "🟡 New";
        case "draft": return "🟠 Draft";
        case "pending": return "🟣 Pending";
        case "published": return "🟢 Published";
        default: return status;
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
    return likes > 1000 ? (likes / 1000).toFixed(1) + "K" : likes;
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
