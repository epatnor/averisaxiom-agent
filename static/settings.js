// settings.js

document.addEventListener("DOMContentLoaded", () => {
    fetchSettings();

    document.querySelectorAll("button").forEach(button => {
        if (button.textContent.toLowerCase().includes("spara")) {
            button.addEventListener("click", saveSettings);
        }
    });
});

function fetchSettings() {
    fetch("/settings")
        .then(res => res.json())
        .then(data => {
            document.querySelectorAll("input, textarea").forEach(el => {
                const key = el.name;
                if (key && data[key] !== undefined) {
                    el.value = data[key];
                }
            });
        })
        .catch(err => console.error("Fel vid hämtning av settings:", err));
}

function saveSettings(event) {
    const card = event.target.closest("div");
    const inputs = card.querySelectorAll("input, textarea");

    const payload = {};
    inputs.forEach(el => {
        if (el.name) payload[el.name] = el.value;
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
