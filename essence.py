# essence.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Undvik ämnen som inte är relevanta för AverisAxiom
UNWANTED_KEYWORDS = ["sports", "soccer", "football", "celebrity", "celebrities", "entertainment", "hollywood"]

def is_relevant(title):
    """Filtrera bort ointressanta ämnen baserat på nyckelord."""
    lower = title.lower()
    return not any(bad in lower for bad in UNWANTED_KEYWORDS)

def cluster_and_summarize(headlines):
    """Sammanfatta och klustra nyheter med GPT, returnera lista med {'title', 'summary'}."""
    if not headlines or not isinstance(headlines, list):
        print("⚠️ Tom eller ogiltig lista av rubriker.")
        return []

    # Sätt ihop prompten
    prompt = f"""
You are an AI news clustering assistant.

You will receive a list of headlines. Your task is to group them into logical clusters based on common topics, then write a brief summary for each cluster.

Return ONLY a valid JSON array of objects, where each object has:
- "title": A short representative title for the cluster.
- "summary": A 2-3 sentence summary of the topic.

Avoid using emojis or special symbols. Write in a neutral, journalistic tone.
DO NOT include any explanation or markdown formatting, just return JSON.

Here are the headlines:

{headlines}
""".strip()

    try:
        # Skicka prompten till GPT
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that returns news topic clusters."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1200,
        )

        content = response.choices[0].message.content.strip()

        # Rensa eventuell markdown-kodblock
        if content.startswith("```json"):
            content = content.removeprefix("```json").removesuffix("```").strip()
        elif content.startswith("```"):
            content = content.removeprefix("```").removesuffix("```").strip()

        # Försök tolka som JSON
        parsed = json.loads(content)

        # Validera och filtrera irrelevanta ämnen
        valid = [
            item for item in parsed
            if isinstance(item, dict) and "title" in item and "summary" in item and is_relevant(item["title"])
        ]

        return valid

    except json.JSONDecodeError as je:
        print("⚠️ Kunde inte tolka JSON från GPT:", je)
        print("Rådata:", content)
        return []

    except Exception as e:
        print("⚠️ Fel vid GPT-anrop:", str(e))
        return []
