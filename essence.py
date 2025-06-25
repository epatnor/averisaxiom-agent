# === File: essence.py ===

import os
import openai

from dotenv import load_dotenv
load_dotenv()


# Skapa OpenAI klient
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def cluster_and_summarize(headlines):
    print("Running AI clustering & summarization...")

    system_prompt = (
        "You are an expert news analyst. Your task is to group related headlines "
        "into major storylines and write a brief summary for each cluster. "
        "Return the output as a JSON list of objects with keys: 'title' and 'summary'."
    )

    user_prompt = "Here are the latest headlines:\n\n"
    for h in headlines:
        user_prompt += f"- {h}\n"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )

    raw_output = response.choices[0].message.content.strip()

    # OBS: vi låtsas att vi får korrekt JSON (i skarp drift ska vi göra bättre felhantering)
    import json
    try:
        clusters = json.loads(raw_output)
        return clusters
    except Exception as e:
        print("Error parsing AI response:", e)
        return []
