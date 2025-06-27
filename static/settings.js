// settings.js

document.addEventListener("DOMContentLoaded", () => {
    loadSettings();

    document.querySelectorAll("button").forEach(button => {
        const label = button.textContent.toLowerCase();
        if (label.includes("save")) button.addEventListener("click", saveSettings);
        if (label.includes("test")) button.addEventListener("click", testSettings);
    });
});

// Load current settings from backend and populate inputs
function loadSettings() {
    fetch("/settings")
        .then(res => res.json())
        .then(data => {
            document.querySelectorAll("input, textarea").forEach(el => {
                const key = el.name;
                if (!key) return;
                if (el.type === "checkbox") {
                    el.checked = Boolean(data[key]);
                } else {
                    el.value = data[key] ?? "";
                }
            });
        })
        .catch(err => console.error("Failed to load settings:", err));
}

// Save settings within the clicked card
function saveSettings(event) {
    const card = event.target.closest(".card, .subcard");
    const inputs = card.querySelectorAll("input, textarea");

    const payload = {};
    inputs.forEach(el => {
        if (!el.name) return;
        payload[el.name] = el.type === "checkbox" ? el.checked : el.value;
    });

    fetch("/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        console.log("Settings saved:", data);
        alert("✅ Settings saved successfully!");
    })
    .catch(err => {
        console.error("Error saving settings:", err);
        alert("❌ Error saving settings.");
    });
}

// Send test request for the clicked card
function testSettings(event) {
    const card = event.target.closest(".card, .subcard");
    const inputs = card.querySelectorAll("input, textarea");

    const payload = {};
    inputs.forEach(el => {
        if (!el.name) return;
        payload[el.name] = el.type === "checkbox" ? el.checked : el.value;
    });

    let endpoint = "/test_scraper";
    const html = card.innerHTML.toLowerCase();
    if (html.includes("youtube")) endpoint = "/test_youtube";
    else if (html.includes("google")) endpoint = "/test_google";

    fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        alert(`✅ Test successful:\n${JSON.stringify(data, null, 2)}`);
    })
    .catch(err => {
        console.error("Error during test:", err);
        alert("❌ Test failed:\n" + err.message);
    });
}
