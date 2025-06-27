// settings.js

// == DOM READY ==
document.addEventListener("DOMContentLoaded", () => {
    loadSettings();

    // 🧷 Bind Save / Test buttons to handlers
    document.querySelectorAll("button").forEach(button => {
        const label = button.textContent.toLowerCase();
        if (label.includes("save")) button.addEventListener("click", saveSettings);
        if (label.includes("test")) button.addEventListener("click", testSettings);
    });
});


// == Load settings from backend and populate inputs ==
function loadSettings() {
    fetch("/settings")
        .then(res => res.json())
        .then(data => {
            document.querySelectorAll("input, textarea").forEach(el => {
                const key = el.name;
                if (!key || !(key in data)) return;

                if (el.type === "checkbox") {
                    el.checked = data[key] === "true" || data[key] === true;
                } else {
                    el.value = data[key] ?? "";
                }
            });
        })
        .catch(err => console.error("❌ Failed to load settings:", err));
}


// == Save settings from current section ==
function saveSettings(event) {
    const card = event.target.closest(".section, .card, .subcard");
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


// == Test feature for current section ==
function testSettings(event) {
    const card = event.target.closest(".section, .card, .subcard");
    if (!card) return;

    const payload = collectInputValues(card);

    let endpoint = "/test_scraper"; // default fallback
    const html = card.innerHTML.toLowerCase();
    if (html.includes("youtube")) endpoint = "/test_youtube";
    else if (html.includes("google")) endpoint = "/test_scraper";

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


// == Collect all inputs from a section/card ==
function collectInputValues(container) {
    const payload = {};
    container.querySelectorAll("input, textarea").forEach(el => {
        if (!el.name) return;
        payload[el.name] = (el.type === "checkbox") ? String(el.checked) : el.value;
    });
    return payload;
}
