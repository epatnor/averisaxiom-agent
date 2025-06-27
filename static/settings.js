// settings.js

// Kör när sidan laddats
document.addEventListener("DOMContentLoaded", () => {
    fetchSettings();

    // Koppla "Spara"-knappar
    document.querySelectorAll("button").forEach(button => {
        if (button.textContent.toLowerCase().includes("spara")) {
            button.addEventListener("click", saveSettings);
        }
    });
});

// Hämtar alla sparade inställningar från backend och fyller i rätt fält
function fetchSettings() {
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
        .catch(err => console.error("Fel vid hämtning av settings:", err));
}

// Sparar alla fält inom det kort som innehåller knappen
function saveSettings(event) {
    const card = event.target.closest(".section");
    const inputs = card.querySelectorAll("input, textarea");

    const payload = {};
    inputs.forEach(el => {
        if (!el.name) return;
        if (el.type === "checkbox") {
            payload[el.name] = el.checked;
        } else {
            payload[el.name] = el.value;
        }
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
