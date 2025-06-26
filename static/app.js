document.addEventListener("DOMContentLoaded", () => {
    loadPosts();

    document.getElementById("generate-draft-btn").addEventListener("click", () => {
        const topic = document.getElementById("creative-topic").value.trim();
        if (!topic) return;
        fetch("/generate_draft", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ topic })
        }).then(loadPosts);
    });

    document.getElementById("run-pipeline-btn").addEventListener("click", () => {
        fetch("/run_pipeline", { method: "POST" }).then(loadPosts);
    });
});

function loadPosts() {
    fetch("/get_posts")
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById("pipeline-list");
            list.innerHTML = "";
            data.forEach((post, index) => {
                const item = document.createElement("div");
                item.className = "list-item";

                const typeLabel = `${typeIcon(post.type)} ${capitalize(post.type)}`;

                item.innerHTML = `
                    <div class="title-snippet" onclick="toggleEditor(${index})">${truncate(post.title, 80)}</div>
                    <div class="status-${post.status.toLowerCase()}">${capitalize(post.status)}</div>
                    <div class="type-${capitalize(post.type)}">${typeLabel}</div>
                    <div class="post-metrics">-</div>
                    <div><button class="small-button" onclick="publishPost(${post.id})">Publish</button></div>
                    <div class="post-editor" id="editor-${index}" style="display:none;">
                        <textarea class="post-editing" id="edit-body-${index}">${post.body || ""}</textarea>
                        <div class="edit-controls">
                            <button class="small-button" onclick="savePost(${post.id}, ${index})">Save</button>
                            <button class="small-button" onclick="cancelEditor(${index})">Cancel</button>
                        </div>
                    </div>
                `;
                list.appendChild(item);
            });
        });
}

function toggleEditor(index) {
    document.getElementById(`editor-${index}`).style.display = "block";
}

function cancelEditor(index) {
    document.getElementById(`editor-${index}`).style.display = "none";
}

function savePost(id, index) {
    const text = document.getElementById(`edit-body-${index}`).value;
    fetch("/save_post", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, text })
    }).then(loadPosts);
}

function publishPost(id) {
    fetch("/publish_post", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id })
    }).then(loadPosts);
}

function typeIcon(type) {
    switch (type?.toLowerCase()) {
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

function capitalize(word) {
    if (!word) return "";
    return word.charAt(0).toUpperCase() + word.slice(1);
}

function truncate(text, maxLength) {
    return text.length > maxLength ? text.slice(0, maxLength - 1) + "…" : text;
}
