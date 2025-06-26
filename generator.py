import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from utils import remove_emojis_and_codeblock

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Genererar en post baserat på en story med title + summary
def generate_post(story):
    prompt = (
        "Skriv ett inlägg baserat på detta ämne.\n"
        "Det ska kännas som en tänkvärd och aktuell observation eller kommentar.\n"
        "Skriv med god ton, inga hashtags, inga emojis, inga frågor – bara ett stilrent inlägg.\n"
        "Håll det gärna inom 300–400 tecken, lite längre än typiska tweets, men inte en blogg.\n\n"
        f"Ämne: {story['title']}\n"
        f"Summering: {story['summary']}\n\n"
        "Text:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                { "role": "system", "content": "Du svarar endast med ren text utan kodblock eller emojis." },
                { "role": "user", "content": prompt }
            ],
            temperature=0.7
        )
        raw = response.choices[0].message.content.strip()
        text = remove_emojis_and_codeblock(raw)
        return text

    except Exception as e:
        print("⚠️ Kunde inte generera inlägg:", e)
        return None

# Förbättrar genererade titlar, eller ersätter med snutt av texten
def generate_better_title(story):
    prompt = (
        "Du är en assistent som skapar korta men specifika rubriker till sociala inlägg.\n"
        "Rubriken får gärna låta som en tidningsrubrik eller en teaser till ämnet.\n"
        "Använd max 10 ord. Undvik generiska titlar som 'AI advances' eller 'Global politics'.\n\n"
        f"Text: {story['summary']}\n\n"
        "Rubrik:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                { "role": "system", "content": "Svara med en enda kort rubrik utan emojis." },
                { "role": "user", "content": prompt }
            ],
            temperature=0.6
        )
        title = remove_emojis_and_codeblock(response.choices[0].message.content.strip())

        # Fall-back om GPT ger något för vagt
        if len(title.split()) < 3 or any(generic in title.lower() for generic in ["politics", "technology", "ai", "news", "update"]):
            title = story['summary'][:60].rstrip('.') + "…"

        return title

    except Exception as e:
        print("⚠️ Kunde inte generera rubrik:", e)
        return story['summary'][:60].rstrip('.') + "…"

# Genererar både titel och text för en story
def generate_full_post(story):
    title = generate_better_title(story)
    body = generate_post(story)
    return {
        "title": title,
        "summary": body
    }
