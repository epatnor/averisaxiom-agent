# generator.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from utils import remove_emojis_and_codeblock  # Importera saneringsfunktion

# Läs in miljövariabler från .env-filen (inkl. OPENAI_API_KEY)
load_dotenv()

# Initiera OpenAI-klient enligt nyare syntax
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_post(title, summary, style=None):
    """
    Skapar ett AI-genererat inlägg baserat på en rubrik och ev. sammanfattning.
    Resultatet är ett kort och sakligt textutkast med en klassificerad typ.
    Om API:t misslyckas eller returnerar ogiltig JSON faller det tillbaka till rubrik/sammanfattning.
    """

    print(f"Generating post for: {title} [auto-type detection]")

    # Systemprompt: styr GPT mot sakligt, koncist språk utan emojis, hype eller clickbait.
    system_prompt = (
        "You are a professional social media assistant.\n"
        "Your task is to generate a short, engaging post from a given topic or summary.\n"
        "Maintain a neutral, journalistic tone.\n"
        "Do not use emojis, hashtags, or symbols.\n"
        "Avoid clickbait, exaggeration, or slang.\n"
        "Keep it concise, factual, and appropriate for an intelligent audience.\n\n"
        "You must also classify what type of post it is. Choose one of:\n"
        "- News\n- Thought\n- Question\n- Satire\n- Creative\n- Raw\n- Rant\n- Joke\n\n"
        "Return only valid JSON in this format:\n"
        "{ \"content\": \"...\", \"type\": \"...\" }"
    )

    # Användarprompt innehåller titel och ev. sammanfattning
    user_prompt = f"Title: {title}\nSummary: {summary or title}"

    try:
        # Skicka prompt till GPT-4o och ta emot svaret
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6
        )

        # Extrahera och sanera svaret
        raw = response.choices[0].message.content.strip()
        print("GPT returned:", raw)

        if not raw:
            raise ValueError("Empty response from GPT")

        cleaned = remove_emojis_and_codeblock(raw)
        parsed = json.loads(cleaned)

        content = parsed.get("content", "").strip()
        post_type = parsed.get("type", "Creative").strip()

    except Exception as e:
        print("⚠️ Failed to parse GPT response:", e)
        content = summary or title
        post_type = "Creative"

    # Returnera som färdigt utkast
    return {
        "title": title,
        "summary": content,
        "status": "draft",
        "type": post_type,
        "comments": 0,
        "likes": 0,
        "shares": 0
    }
