// app.js

const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    loadPipeline();
    loadStats();

    document.getElementById("automatic-btn").addEventListener("click", runAutomatic);
    document.getElementById("generate-btn").addEventListener("click", generateDraft);
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

        // Expansion på klick av titel
        row.querySelector(".title-snippet").addEventListener("click", () => toggleRowExpand(row, item));

        // Knyt knapparnas funktioner
        row.querySelectorAll(".small-button").forEach(btn => {
            if (btn.innerText === "Edit") {
                btn.addEventListener("click", (e) => {
                    e.stopPropagation();
                    editPost(item);
                });
            }
            // Fler knappar kan kopplas här om vi vill
        });

        list.appendChild(row);
    });
}

function toggleRowExpand(row, item) {
    const expanded = row.classList.contains("expanded");
    if (expanded) {
        row.classList.remove("expanded");
        row.querySelector(".title-snippet").innerText = item.title;
    } else {
        row.classList.add("expanded");
        row.querySelector(".title-snippet").innerText = `${item.title}\n\n${item.summary}`;
    }
}

function editPost(item) {
    alert("Edit clicked for:\n\n" + item.title + "\n\n" + item.summary);
}

function generateActionButtons(item) {
    if (item.status === "New") {
        return `<button class="small-button">Generate Draft</button>`;
    } else if (item.status === "Draft") {
        return `<button class="small-button">Publish</button>
                <button class="small-button">Edit</button>
                <button class="small-button">Delete</button>`;
    } else if (item.status === "Pending") {
        return `<button class="small-button">Post</button>
                <button class="small-button">Edit</button>
                <button class="small-button">Delete</button>`;
    } else if (item.status === "Published") {
        return `<button class="small-button">View</button>
                <button class="small-button disabled">Update Stats</button>`;
    }
    return "";
}

function statusEmoji(status) {
    switch (status) {
        case "New": return "🟡";
        case "Draft": return "🟠";
        case "Pending": return "🟣";
        case "Published": return "🟢";
        default: return "";
    }
}

function statusClass(status) {
    return `status-${status.toLowerCase()}`;
}

function capitalize(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

function formatLikes(likes) {
    return likes >= 1000 ? (likes / 1000).toFixed(1) + "K" : likes;
}

function runAutomatic() {
    fetch(`${API_URL}/run_automatic_pipeline`, { method: "POST" })
        .then(() => loadPipeline());
}

function generateDraft() {
    const topic = document.getElementById("creative-topic").value;
    if (!topic) {
        alert("Enter a topic first");
        return;
    }
    fetch(`${API_URL}/generate_draft`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: topic, summary: "", style: "News" })
    })
    .then(() => loadPipeline());
}

function loadStats() {
    // Placeholder - kommer sen
}
