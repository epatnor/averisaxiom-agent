# essence.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from utils import remove_emojis_and_codeblock

# Läs in API-nyckel från .env
load_dotenv()

# Initiera OpenAI-klient
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_clustered_storylines(topics):
    """
    Tar en lista av dicts med "title" och "summary", och grupperar dem tematiskt
    med hjälp av GPT. Returnerar en lista av teman där varje tema har en rubrik
    och en sammanfattning.
    
    Exempel på input:
    [
        { "title": "Elon Musk släpper ny robot", "summary": "Tesla presenterar..." },
        { "title": "USA bombar Iran", "summary": "Enligt rapporter från..." }
    ]
    
    Exempel på output:
    [
        { "title": "Teknologiska framsteg", "summary": "Flera nyheter kretsar kring AI och robotik." },
        { "title": "Geopolitiska spänningar", "summary": "Iran och USA är åter i fokus." }
    ]
    """
    
    # Bygg upp prompten till GPT
    prompt = (
        "Du är en analytisk assistent som grupperar nyhetsrubriker efter tema.\n"
        "För varje grupp, skapa en titel och en kort summering (1-2 meningar).\n"
        "Returnera resultatet som en JSON-array:\n\n"
        "[\n"
        "  { \"title\": \"Tema A\", \"summary\": \"Kort summering...\" },\n"
        "  ...\n"
        "]\n\n"
        "Här är indata:\n\n"
    )

    for t in topics:
        prompt += f"- {t['title']}: {t['summary']}\n"

    try:
        # Skicka prompt till GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                { "role": "system", "content": "Du svarar alltid endast med giltig JSON." },
                { "role": "user", "content": prompt }
            ],
            temperature=0.5
        )

        # Rått svar från GPT
        raw = response.choices[0].message.content.strip()
        print("GPT clustering raw response:", raw)

        # Sanera och parsa svaret
        cleaned = remove_emojis_and_codeblock(raw)
        parsed = json.loads(cleaned)
        return parsed

    except Exception as e:
        print("⚠️ Kunde inte tolka JSON från GPT:", e)
        print("Rådata:", raw)
        return []
