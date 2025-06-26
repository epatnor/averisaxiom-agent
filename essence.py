# essence.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Ladda .env om det behövs (valfritt)
load_dotenv()

# Initiera klient enligt nya openai>=1.0.0 formatet
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def cluster_and_summarize(headlines):
    """
    Tar en lista av nyhetsrubriker och returnerar grupperade ämneskluster med sammanfattningar.
    Använder GPT för att skapa en JSON-struktur med {title, summary}-objekt.
    """
    if not headlines:
        return []

    # Skapa prompten för GPT
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
            max_tokens=1000,
        )

        content = response.choices[0].message.content.strip()
        return json.loads(content)

    except Exception as e:
        print("⚠️ GPT clustering failed:", str(e))
        return []
