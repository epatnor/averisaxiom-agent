// settings.js

// == DOM READY ==
document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 DOM ready, initializing settings.js...");
    loadSettings();

    // 🧷 Bind Save / Test / Reset buttons to handlers
    document.querySelectorAll("button").forEach(button => {
        const label = button.textContent.toLowerCase();
        if (label.includes("save")) button.addEventListener("click", saveSettings);
        if (label.includes("test")) button.addEventListener("click", testSettings);
        if (label.includes("reset")) button.addEventListener("click", resetDefaults);
    });
});


// == Load settings from backend and populate inputs ==
function loadSettings() {
    console.log("📡 Attempting to fetch /settings...");
    fetch("/settings")
        .then(res => {
            console.log("🌐 Response status:", res.status);
            return res.json();
        })
        .then(data => {
            console.log("✅ Settings loaded:", data);

            const inputs = document.querySelectorAll("input, textarea");
            console.log(`🔎 Found ${inputs.length} input/textarea elements.`);

            inputs.forEach(el => {
                const key = el.name;
                if (!key) {
                    console.warn("⚠️ Input element missing 'name' attribute:", el);
                    return;
                }

                if (!(key in data)) {
                    console.warn(`⚠️ No value returned for key '${key}'`);
                    return;
                }

                if (el.type === "checkbox") {
                    el.checked = (data[key] === "true" || data[key] === true);
                } else {
                    el.value = data[key] ?? "";
                }

                console.log(`↪️ Set [${key}] to`, el.type === "checkbox" ? el.checked : el.value);
            });
        })
        .catch(err => console.error("❌ Failed to load settings:", err));
}


// == Save settings from current section ==
function saveSettings(event) {
    const card = event.target.closest(".section, .card, .subcard");
    if (!card) return;

    const payload = collectInputValues(card);
    console.log("💾 Saving settings:", payload);

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
    console.log("🧪 Testing settings:", payload);

    let endpoint = "/test_scraper"; // fallback default
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


// == Reset handler (just reloads the page for now) ==
function resetDefaults() {
    if (confirm("Reset settings to default values from .env?")) {
        location.reload();
    }
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
