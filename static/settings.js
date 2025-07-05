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
    .then(res => res.json())
    .then(data => {
      console.log("✅ Settings loaded:", data);
      const inputs = [...document.querySelectorAll("input[name], textarea[name]")];
      const normalized = {};
      Object.entries(data).forEach(([k, v]) => {
        normalized[k.trim().toUpperCase()] = v;
      });

      inputs.forEach(el => {
        const key = el.name?.toUpperCase();
        const val = normalized[key];

        if (key === undefined || val === undefined) return;

        if (el.type === "checkbox") {
          el.checked = val === true || val === "true";
        } else {
          if (shouldMask(key, val)) {
            el.value = maskValue(val);
            el.setAttribute("data-masked", "true");
          } else {
            el.value = val ?? "";
            el.removeAttribute("data-masked");
          }
        }

        if (isDummyValue(val)) {
          el.classList.add("dummy");
          el.title = "This appears to be a placeholder value. Please update.";
        } else {
          el.classList.remove("dummy");
          el.removeAttribute("title");
        }
      });

      updateStatusDots(); // ✅ update pluppar efter load
    })
    .catch(err => console.error("❌ Failed to load settings:", err));
}

// == Dummy-check ==
function isDummyValue(val) {
  if (!val || typeof val !== "string") return true;
  const dummyPatterns = [
    "your-openai-key-here", "example.com", "proxy.example",
    "bluesky-app-password-here", "mastodon-access-token-here",
    "youtube-api-key-here", "serper-api-key-here", "bsky.social"
  ];
  return dummyPatterns.some(p => val.includes(p));
}

// == Mask detection ==
function shouldMask(key, val) {
  if (!val || typeof val !== "string") return false;
  const sensitive = [
    "OPENAI_API_KEY", "SERPER_API_KEY", "YOUTUBE_API_KEY",
    "MASTODON_ACCESS_TOKEN", "BLUESKY_APP_PASSWORD"
  ];
  return sensitive.includes(key) && val.length > 8;
}

function maskValue(val) {
  if (val.length <= 8) return "••••••••";
  return `${val.slice(0, 4)}...${val.slice(-4)}`;
}

// == Save Settings ==
function saveSettings(event) {
  const section = event.target.closest(".section");
  if (!section) return;
  const payload = collectInputValues(section);
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

// == Test Settings ==
function testSettings(event) {
  const section = event.target.closest(".section");
  if (!section) return;
  const payload = collectInputValues(section);
  const html = section.innerHTML.toLowerCase();
  const endpoint = html.includes("youtube") ? "/test_youtube" : "/test_scraper";

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

// == Reset ==
function resetDefaults() {
  if (confirm("Reset settings to default values from .env?")) {
    location.reload();
  }
}

// == Input value collection ==
function collectInputValues(container) {
  const result = {};
  container.querySelectorAll("input[name], textarea[name]").forEach(el => {
    const key = el.name.trim().toUpperCase();
    if (el.type === "checkbox") {
      result[key] = String(el.checked);
    } else {
      const raw = el.value.trim();
      const masked = el.getAttribute("data-masked") === "true";
      result[key] = (masked && raw.includes("...")) ? "" : raw;
    }
  });
  return result;
}

// == Update all status pluppar ==
function updateStatusDots() {
  updateDot("dot-google", ["GOOGLE_RSS_URL", "GOOGLE_MAX_AGE", "GOOGLE_MAX_ITEMS"]);
  updateDot("dot-youtube", ["YOUTUBE_FEED_URL", "YOUTUBE_API_KEY"]);
  updateDot("dot-api", ["OPENAI_API_KEY", "SERPER_API_KEY"]);
  updatePlatformDot();
  document.getElementById("dot-system").className = "status-dot ok"; // system always green
}

// == Dot logic for regular field groups ==
function updateDot(dotId, fieldNames) {
  const dot = document.getElementById(dotId);
  if (!dot) return;
  const all = fieldNames.map(name => document.querySelector(`[name="${name}"]`));
  const anyMissing = all.some(el => el === null);
  const anyEmpty = all.some(el => !el?.value.trim());

  dot.className = "status-dot " + (
    anyMissing ? "error" :
    anyEmpty ? "warn" : "ok"
  );
}

// == Special dot logic for publishing platforms ==
function updatePlatformDot() {
  const dot = document.getElementById("dot-platforms");
  if (!dot) return;

  const platforms = [
    {
      flag: "USE_X",
      required: []
    },
    {
      flag: "USE_BLUESKY",
      required: ["BLUESKY_HANDLE", "BLUESKY_APP_PASSWORD"]
    },
    {
      flag: "USE_MASTODON",
      required: ["MASTODON_BASE_URL", "MASTODON_ACCESS_TOKEN"]
    }
  ];

  let worst = "warn"; // default is yellow if nothing is filled
  for (const p of platforms) {
    const enabled = document.querySelector(`[name="${p.flag}"]`)?.checked;
    if (!enabled) continue;

    const requiredInputs = p.required.map(name => document.querySelector(`[name="${name}"]`));
    if (requiredInputs.some(el => el === null)) {
      worst = "error";
      break;
    }
    if (requiredInputs.some(el => !el.value.trim())) {
      worst = "warn";
    } else {
      worst = "ok";
      break;
    }
  }

  dot.className = "status-dot " + worst;
}
