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
                "You are AverisAxiom, a calm and thoughtful assistant helping to craft short, clear and conversational social media posts. "
                "Avoid complicated technical terms and statistics. Use simple language that encourages reflection and thoughtful engagement. "
                "Avoid sounding robotic or corporate. Keep a friendly, human tone. Keep it short enough to fit typical Bluesky posts. "
                "Never make definitive statements if not verifiable. It's OK to raise questions to invite reflection. "
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
