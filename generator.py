# generator.py

import os
import openai
import json
from dotenv import load_dotenv

# Ladda miljövariabler från .env-fil (inkl. OPENAI_API_KEY)
load_dotenv()

# Initiera OpenAI-klienten
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_post(title, summary, style=None):
    """
    Skapar ett AI-genererat inlägg baserat på en rubrik och ev. sammanfattning.
    Returnerar en dikt med postens titel, text, typ och metadata.
    """

    print(f"Generating post for: {title} [auto-type detection]")

    # Prompt till GPT som instruerar den att hålla sig till saklig ton – inga emojis, inga hashtags
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

    # Skicka in rubrik och sammanfattning som användarinput
    user_prompt = f"Title: {title}\nSummary: {summary or title}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6
        )

        # Försök parsa JSON-svaret
        raw = response.choices[0].message.content.strip()
        print("GPT returned:", raw)

        parsed = json.loads(raw)
        content = parsed.get("content", "").strip()
        post_type = parsed.get("type", "Creative").strip()

    except Exception as e:
        print("⚠️ Failed to parse GPT response:", e)
        content = summary or title
        post_type = "Creative"

    return {
        "title": title,
        "summary": content,
        "status": "draft",
        "type": post_type,
        "comments": 0,
        "likes": 0,
        "shares": 0
    }
