// 🧠 Entry point when the page loads
document.addEventListener("DOMContentLoaded", () => {
    loadPosts();

    document.getElementById("generate-draft-btn").addEventListener("click", () => {
        const topic = document.getElementById("creative-topic").value.trim();
        if (topic) {
            generateDraft(topic);
        }
    });

    document.getElementById("run-pipeline-btn").addEventListener("click", () => {
        runAutomaticPipeline();
    });
});

// 🌈 Icon lookup for post type
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

// 🎯 Load posts from backend
async function loadPosts() {
    try {
        const res = await fetch("/get_posts");
        if (!res.ok) throw new Error(`Failed to fetch posts: ${res.statusText}`);
        const posts = await res.json();
        renderPostList(posts);
    } catch (error) {
        console.error("Error loading posts:", error);
        document.getElementById("pipeline-list").innerHTML = `<div style="color:red;">Failed to load posts</div>`;
    }
}

// 🎨 Render each post row into the UI
function renderPostList(posts) {
    const container = document.getElementById("pipeline-list");
    container.innerHTML = "";

    posts.forEach(post => {
        const row = document.createElement("div");
        row.className = "list-item";

        const title = document.createElement("div");
        title.className = "title-snippet";
        title.textContent = post.title || "(Untitled)";

        const status = document.createElement("div");
        status.className = `status-${post.status?.toLowerCase() || "unknown"}`;
        status.textContent = post.status || "-";

        const type = document.createElement("div");
        type.className = `type-${post.type || "unknown"}`;
        type.innerHTML = `${typeIcon(post.type)} <span>${post.type || "-"}</span>`;

        const metrics = document.createElement("div");
        metrics.className = "post-metrics";
        metrics.textContent = "-";

        const action = document.createElement("div");
        const btn = document.createElement("button");
        btn.textContent = "Publish";
        btn.className = "small-button";
        btn.onclick = () => publishPost(post.id);
        action.appendChild(btn);

        row.appendChild(title);
        row.appendChild(status);
        row.appendChild(type);
        row.appendChild(metrics);
        row.appendChild(action);
        container.appendChild(row);
    });
}

// ✨ Generate a creative draft post
async function generateDraft(topic) {
    try {
        const res = await fetch("/generate_draft", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ topic })
        });

        if (!res.ok) throw new Error("Failed to generate draft");

        const data = await res.json();
        console.log("Draft generated:", data);
        loadPosts();
    } catch (error) {
        console.error("Error generating draft:", error);
    }
}

// 🤖 Run automatic news-based generation
async function runAutomaticPipeline() {
    try {
        const res = await fetch("/run_pipeline", { method: "POST" });
        if (!res.ok) throw new Error("Pipeline execution failed");

        const result = await res.json();
        console.log("Pipeline complete:", result);
        loadPosts();
    } catch (error) {
        console.error("Error running pipeline:", error);
    }
}

// 🚀 Publish a draft post
async function publishPost(id) {
    try {
        const res = await fetch(`/publish_post/${id}`, { method: "POST" });
        if (!res.ok) throw new Error("Failed to publish post");
        loadPosts();
    } catch (error) {
        console.error("Error publishing post:", error);
    }
}
