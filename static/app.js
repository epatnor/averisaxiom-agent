
const API = "http://localhost:8000";

function runPipeline() {
    fetch(API + "/run_automatic_pipeline", {method: "POST"}).then(loadPipeline);
}

function loadPipeline() {
    fetch(API + "/pipeline")
        .then(r => r.json())
        .then(data => {
            const list = document.getElementById("list");
            list.innerHTML = "";
            data.forEach(item => {
                const div = document.createElement("div");
                div.className = "list-item";
                div.innerText = `[${item.status}] ${item.source}: ${item.title}`;
                list.appendChild(div);
            });
        });
}

document.addEventListener("DOMContentLoaded", loadPipeline);
