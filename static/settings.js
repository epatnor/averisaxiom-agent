// settings.js

// On DOM ready, load settings and bind button events
document.addEventListener("DOMContentLoaded", () => {
    loadSettings();

    // Attach save/test handlers based on button label
    document.querySelectorAll("button").forEach(button => {
        const label = button.textContent.toLowerCase();
        if (label.includes("save")) button.addEventListener("click", saveSettings);
        if (label.includes("test")) button.addEventListener("click", testSettings);
    });
});

// Load settings from backend and populate matching input fields
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
        .catch(err => console.error("❌ Failed to load settings:", err));
}

// Save settings for a specific section (card or subcard)
function saveSettings(event) {
    const card = event.target.closest(".card, .subcard");
    if (!card) return;

    const payload = collectInputValues(card);

    fetch("/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        console.log("✅ Settings saved:", data);
        alert("✅ Settings saved successfully!");
    })
    .catch(err => {
        console.error("❌ Error saving settings:", err);
        alert("❌ Error saving settings.");
    });
}

// Send test request based on card type
function testSettings(event) {
    const card = event.target.closest(".card, .subcard");
    if (!card) return;

    const payload = collectInputValues(card);

    // Pick endpoint based on inner content
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
        console.error("❌ Test failed:", err);
        alert("❌ Test failed:\n" + err.message);
    });
}

// Utility: Collect input values from a card into an object
function collectInputValues(card) {
    const payload = {};
    const inputs = card.querySelectorAll("input, textarea");
    inputs.forEach(el => {
        if (!el.name) return;
        payload[el.name] = el.type === "checkbox" ? el.checked : el.value;
    });
    return payload;
}
