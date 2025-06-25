
const API_URL = "";

document.addEventListener("DOMContentLoaded", () => { loadPipeline(); });

function runAutomatic() {
    fetch("/run_automatic_pipeline", { method: "POST" }).then(() => loadPipeline());
}

function loadPipeline() {
    fetch("/pipeline").then(res => res.json()).then(data => {
        const list = document.getElementById("pipeline-list");
        list.innerHTML = "";
        data.forEach(item => {
            list.innerHTML += `<div>${item.title} [${item.status}]</div>`;
        });
    });
}

function generateDraft() {
    const topic = document.getElementById("creative-topic").value;
    fetch("/generate_draft", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({title: topic, summary: ""})
    }).then(() => loadPipeline());
}

function saveSettings() {
    const prompt = document.getElementById("base-prompt").value;
    fetch("/settings", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"base_prompt": prompt})
    });
}
