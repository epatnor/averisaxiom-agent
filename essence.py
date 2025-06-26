# essence.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Ladda miljövariabler från .env-fil
load_dotenv()

# Initiera OpenAI-klienten (kräver openai>=1.0.0)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def cluster_and_summarize(headlines):
    """
    Tar en lista av rubriker och returnerar JSON-struktur med ämneskluster:
    [{ "title": "...", "summary": "..." }, ...]
    Om något går fel returneras en tom lista.
    """

    if not headlines or not isinstance(headlines, list):
        print("⚠️ Tom eller ogiltig lista av rubriker.")
        return []

    # Format för prompt till GPT
    prompt = f"""
You are an AI news clustering assistant.

You will receive a list of headlines. Your task is to group them into logical clusters based on common topics, then write a brief summary for each cluster.

Return ONLY a valid JSON array of objects, where each object has:
- "title": A short representative title for the cluster.
- "summary": A 2-3 sentence summary of the topic.

Avoid using emojis or special symbols. Write in neutral, journalistic tone.

DO NOT include any explanation, just return pure JSON.

Here are the headlines:

{headlines}
""".strip()

    try:
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
        
        # Verifiera JSON-format
        parsed = json.loads(content)

        # Extra kontroll: ska vara lista med dicts innehållande title & summary
        if isinstance(parsed, list) and all(isinstance(p, dict) and "title" in p and "summary" in p for p in parsed):
            return parsed
        else:
            print("⚠️ Ogiltig JSON-struktur:", parsed)
            return []

    except json.JSONDecodeError as je:
        print("⚠️ Kunde inte tolka JSON från GPT:", je)
        print("Rådata:", content)
        return []

    except Exception as e:
        print("⚠️ Fel vid GPT-anrop:", str(e))
        return []
