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

            // Update all inputs with their corresponding values
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
                    // Show masked value for sensitive fields
                    if (shouldMask(key, val)) {
                        el.value = maskValue(val);
                        el.setAttribute("data-masked", "true");
                    } else {
                        el.value = val ?? "";
                        el.removeAttribute("data-masked");
                    }
                }

                // Style and tooltip if it's a dummy value
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

// Determine if a setting key should be masked in the UI
function shouldMask(key, val) {
    if (!val || typeof val !== "string") return false;
    const sensitiveKeys = [
        "OPENAI_API_KEY", "SERPER_API_KEY", "YOUTUBE_API_KEY",
        "MASTODON_ACCESS_TOKEN", "BLUESKY_APP_PASSWORD"
    ];
    return sensitiveKeys.includes(key) && val.length > 8;
}

// Return a masked representation of a value like: abc...xyz
function maskValue(val) {
    if (val.length <= 8) return "••••••••";
    return `${val.slice(0, 4)}...${val.slice(-4)}`;
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
        const key = el.name.trim().toUpperCase();
        if (el.type === "checkbox") {
            payload[key] = String(el.checked);
        } else {
            const raw = el.value.trim();
            const wasMasked = el.getAttribute("data-masked") === "true";
            payload[key] = (wasMasked && raw.includes("...")) ? "" : raw;
        }
    });
    return payload;
}

updateStatusDots();

function updateStatusDots() {
  // === Google ===
  const googleFields = ["GOOGLE_RSS_URL", "GOOGLE_MAX_AGE", "GOOGLE_MAX_ITEMS"];
  updateDot("dot-google", googleFields);

  // === YouTube ===
  const ytFields = ["YOUTUBE_FEED_URL", "YOUTUBE_API_KEY"];
  updateDot("dot-youtube", ytFields);

  // === API Keys ===
  const apiFields = ["OPENAI_API_KEY", "SERPER_API_KEY"];
  updateDot("dot-api", apiFields);

  // === Platforms ===
  const platforms = ["USE_X", "USE_BLUESKY", "USE_MASTODON"];
  const anySelected = platforms.some(name => document.querySelector(`[name="${name}"]`)?.checked);
  const dot = document.getElementById("dot-platforms");
  dot.className = "status-dot " + (anySelected ? "ok" : "warn");

  // === System ===
  document.getElementById("dot-system").className = "status-dot ok"; // always green for now
}

function updateDot(dotId, fieldNames) {
  const dot = document.getElementById(dotId);
  const all = fieldNames.map(name => document.querySelector(`[name="${name}"]`));
  const anyEmpty = all.some(el => !el || !el.value.trim());
  const anyMissing = all.some(el => el === null);

  if (anyMissing) {
    dot.className = "status-dot error";
  } else if (anyEmpty) {
    dot.className = "status-dot warn";
  } else {
    dot.className = "status-dot ok";
  }
}
