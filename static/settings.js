// settings.js

document.addEventListener("DOMContentLoaded", () => {
    fetchSettings();

    document.querySelectorAll("button").forEach(button => {
        const label = button.textContent.toLowerCase();
        if (label.includes("spara")) button.addEventListener("click", saveSettings);
        if (label.includes("testa")) button.addEventListener("click", testSettings);
    });
});

// Hämtar sparade settings från backend
function fetchSettings() {
    fetch("/settings")
        .then(res => res.json())
        .then(data => {
            document.querySelectorAll("input, textarea").forEach(el => {
                const key = el.name;
                if (!key) return;
                if (el.type === "checkbox") el.checked = Boolean(data[key]);
                else el.value = data[key] ?? "";
            });
        })
        .catch(err => console.error("Fel vid hämtning av settings:", err));
}

// Sparar inställningar inom ett kort
function saveSettings(event) {
    const card = event.target.closest(".section");
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
        console.log("Inställningar sparade:", data);
        alert("Inställningar sparade!");
    })
    .catch(err => console.error("Fel vid sparning:", err));
}

// Testar inställningar för en sektion
function testSettings(event) {
    const card = event.target.closest(".section");
    const inputs = card.querySelectorAll("input, textarea");

    const payload = {};
    inputs.forEach(el => {
        if (!el.name) return;
        payload[el.name] = el.type === "checkbox" ? el.checked : el.value;
    });

    // Enkel heuristik för att bestämma vilken test-endpoint vi ska träffa
    let endpoint = "/test_scraper";
    if (card.innerHTML.includes("YouTube")) endpoint = "/test_youtube";

    fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        alert(`✅ Test lyckades:\n${JSON.stringify(data, null, 2)}`);
    })
    .catch(err => {
        console.error("Fel vid testning:", err);
        alert("❌ Fel vid testning:\n" + err.message);
    });
}
