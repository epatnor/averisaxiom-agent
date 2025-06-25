const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    loadPipeline();

    // Knyt knappar direkt när sidan laddas
    document.getElementById("run-automatic-btn").addEventListener("click", () => {
        runAutomatic();
    });

    // Vi kan på samma sätt knyta andra knappar här framöver
});

function loadPipeline() {
    fetch(`${API_URL}/pipeline`)
        .then(res => res.json())
        .then(data => renderPipeline(data.concat(dummyPosts())))
        .catch(() => renderPipeline(dummyPosts()));
}

function dummyPosts() {
    return [
        { id: 1, title: "BREAKING: US strikes Iranian nuclear facility...", summary: "Short summary", status: "New", type: "Auto", comments: 0, likes: 0, shares: 0 },
        { id: 2, title: "AI Conference 2025 creative preview...", summary: "Short summary", status: "Draft", type: "Creative", comments: 0, likes: 0, shares: 0 },
        { id: 3, title: "NASA's Artemis mission lands crew on Moon...", summary: "Summary text", status: "Published", type: "Auto", comments: 312, likes: 5100, shares: 980 }
    ];
}

function renderPipeline(data) {
    const list = document.getElementById("pipeline-list");
    list.innerHTML = "";

    data.forEach(item => {
        const div = document.createElement("div");
        div.className = "list-item";
        div.innerHTML = `
            <div class="title-snippet">${item.title}</div>
            <div class="status-${item.status.toLowerCase()}">${statusEmoji(item.status)} ${item.status}</div>
            <div class="type-${item.type.toLowerCase()}">${item.type}</div>
            <div class="metrics">${formatMetrics(item)}</div>
            <div class="action-buttons">${actionButtons(item)}</div>
        `;
        list.appendChild(div);
    });
}

function actionButtons(item) {
    if (item.status === "New") {
        return `<button class='small-button'>Generate Draft</button>`;
    } else if (item.status === "Draft" || item.status === "Pending") {
        return `
            <button class='small-button'>Publish</button>
            <button class='small-button' onclick="expandRow(${item.id})">Edit</button>
            <button class='small-button'>Delete</button>
        `;
    } else if (item.status === "Published") {
        return `
            <button class='small-button'>View</button>
            <button class='small-button disabled'>Update Stats</button>
        `;
    }
    return "";
}

function expandRow(id) {
    const list = document.getElementById("pipeline-list");
    const allItems = list.getElementsByClassName("list-item");

    Array.from(allItems).forEach(div => {
        if (div.dataset.expanded === "true") {
            div.classList.remove("expanded");
            div.dataset.expanded = "false";
            const existing = div.querySelector(".expanded-content");
            if (existing) existing.remove();
        }
    });

    const row = Array.from(allItems).find(div => div.innerHTML.includes(`expandRow(${id})`));
    if (row) {
        row.dataset.expanded = "true";
        const expanded = document.createElement("div");
        expanded.className = "expanded-content";
        expanded.style.marginTop = "10px";
        expanded.style.padding = "10px";
        expanded.style.backgroundColor = "#1a1a1a";
        expanded.innerHTML = `
            <label>Title:</label><br>
            <input type="text" style="width: 100%;" value="${row.querySelector('.title-snippet').textContent}"><br><br>
            <label>Summary:</label><br>
            <textarea style="width: 100%; height: 80px;">[Summary placeholder]</textarea><br><br>
            <button class="small-button">Save</button>
            <button class="small-button">Cancel</button>
        `;
        row.appendChild(expanded);
        row.classList.add("expanded");
    }
}

function formatMetrics(item) {
    if (item.status !== "Published") return "-";
    return `💬${item.comments} ❤️${formatLikes(item.likes)} 🔁${item.shares}`;
}

function formatLikes(likes) {
    return likes > 1000 ? (likes / 1000).toFixed(1) + "K" : likes;
}

function statusEmoji(status) {
    switch(status) {
        case "New": return "🟡";
        case "Draft": return "🟠";
        case "Pending": return "🟣";
        case "Published": return "🟢";
        default: return "";
    }
}

function runAutomatic() {
    console.log("Running automatic pipeline...");
    fetch(`${API_URL}/run_automatic_pipeline`, { method: "POST" })
        .then(() => {
            console.log("Pipeline complete");
            loadPipeline();
        })
        .catch(err => {
            console.error("Pipeline failed", err);
        });
}
