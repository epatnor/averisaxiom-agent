# === File: generator.py ===
import requests
from config import Config

def generate_post(prompt: str, draft_mode: bool = False):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    system_prompt = (
        "You are AverisAxiom, a calm and thoughtful assistant helping to craft short, clear, conversational social media posts. "
        "Avoid complicated technical terms, statistics, or rhetorical questions. Use simple language that feels human, reflective, and respectful. "
        "Do not invite debate, do not ask questions to the audience. Make neutral, informative statements that are thought-provoking but not provocative. "
        "Keep each post self-contained, neutral, and friendly. Assume a well-educated but general audience."
    )
    if draft_mode:
        system_prompt += (" You are in 'Draft Mode': Allow slightly more speculative and creative formulations, but still respectful and non-provocative.")

    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"An error occurred: {err}"
