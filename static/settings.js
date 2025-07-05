// settings.js

// Wait for DOM to be ready
document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 DOM ready, initializing settings.js...");
    loadSettings();

    // Bind Save / Test / Reset buttons
    document.querySelectorAll("button").forEach(button => {
        const label = button.textContent.toLowerCase();
        if (label.includes("save")) button.addEventListener("click", saveSettings);
        if (label.includes("test")) button.addEventListener("click", testSettings);
        if (label.includes("reset")) button.addEventListener("click", resetDefaults);
    });
});

// Load settings from backend and populate input fields
function loadSettings() {
    console.log("📡 Attempting to fetch /settings...");
    fetch("/settings")
        .then(res => {
            console.log("🌐 Response status:", res.status);
            return res.json();
        })
        .then(data => {
            console.log("✅ Settings loaded:", data);

            const inputs = [...document.querySelectorAll("input[name], textarea[name]")];
            console.log(`🔎 Found ${inputs.length} named input/textarea elements.`);

            const normalizedData = {};
            Object.entries(data).forEach(([k, v]) => {
                normalizedData[k.trim().toUpperCase()] = v;
            });

            inputs.forEach(el => {
                const rawName = el.name;
                const key = rawName?.toUpperCase();
                if (!(key in normalizedData)) {
                    console.warn(`⚠️ No value returned for key '${key}'`);
                    return;
                }

                const val = normalizedData[key];
                if (el.type === "checkbox") {
                    el.checked = (val === true || val === "true");
                } else {
                    el.value = val ?? "";
                }

                // Check if value looks like a dummy
                if (isDummyValue(val)) {
                    el.classList.add("dummy");
                    el.title = "This appears to be a placeholder value. Please update.";
                } else {
                    el.classList.remove("dummy");
                    el.removeAttribute("title");
                }

                console.log(`↪️ Set [${key}] to`, el.type === "checkbox" ? el.checked : `"${el.value}"`);
            });
        })
        .catch(err => console.error("❌ Failed to load settings:", err));
}

// Determine if a value is considered a dummy/placeholder
function isDummyValue(val) {
    if (!val || typeof val !== "string") return true;
    const dummyPatterns = [
        "your-openai-key-here", "example.com", "proxy.example",
        "bluesky-app-password-here", "mastodon-access-token-here",
        "youtube-api-key-here", "serper-api-key-here", "bsky.social"
    ];
    return dummyPatterns.some(pattern => val.includes(pattern));
}

// Save settings from a specific section/card
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

// Run test endpoint for a section based on context
function testSettings(event) {
    const card = event.target.closest(".section, .card, .subcard");
    if (!card) return;

    const payload = collectInputValues(card);
    console.log("🧪 Testing settings:", payload);

    let endpoint = "/test_scraper";
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

// Reload the page to reset settings
function resetDefaults() {
    if (confirm("Reset settings to default values from .env?")) {
        location.reload();
    }
}

// Collect all named inputs in a given container
function collectInputValues(container) {
    const payload = {};
    container.querySelectorAll("input[name], textarea[name]").forEach(el => {
        payload[el.name.trim().toUpperCase()] = (el.type === "checkbox") ? String(el.checked) : el.value;
    });
    return payload;
}
