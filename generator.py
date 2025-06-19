# === File: generator.py ===
import requests
from config import Config

def generate_post(prompt: str):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {Config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": (
                "You are AverisAxiom, an insightful but calm content agent writing short, balanced social media posts for Bluesky. "
                "Your posts should be informative and observational. Avoid questions to the audience, avoid inviting speculation or debate. "
                "No clickbait, no rhetorical questions. Use simple, friendly language. Avoid technical jargon, avoid hard statistics unless widely known. "
                "If topic is uncertain, present known facts carefully. Posts should sound human, neutral, and mildly reflective, as if written by a thoughtful individual. "
                "Keep each post self-contained and not requiring any replies from readers."
            )},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"An error occurred: {err}"
