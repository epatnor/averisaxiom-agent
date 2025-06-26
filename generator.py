# generator.py

import os
import openai
import json
from dotenv import load_dotenv
from utils import remove_emojis_and_codeblock

# Load API key from .env
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_post(topic, summary, style=None):
    """Generates a social media post with a precise, informative title and brief summary."""

    print(f"Generating post for: {topic} [style: {style}]")

    system_prompt = (
        "You are a social media writing assistant creating short, intelligent posts.\n"
        "Your task is to:\n"
        "- Write a distinct, highly specific title that includes names, places, or unique events.\n"
        "- Avoid vague or generic themes like 'Global Politics' or 'Tech News'.\n"
        "- Focus on clarity and information value in the title (like a news headline).\n"
        "- Write a 2–3 sentence content summary that is neutral and factual.\n"
        "- Do not include hashtags, emojis, or formatting.\n"
        "- Return ONLY valid JSON:\n"
        "{ \"title\": \"...\", \"content\": \"...\", \"type\": \"...\" }\n"
        "Post type must be one of: News, Thought, Question, Satire, Creative, Raw, Rant, Joke."
    )

    user_prompt = f"Topic: {topic}\nSummary: {summary or topic}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6
        )

        raw = response.choices[0].message.content.strip()
        print("GPT returned:", raw)

        if not raw:
            raise ValueError("Empty response from GPT")

        cleaned = remove_emojis_and_codeblock(raw)
        parsed = json.loads(cleaned)

        title = parsed.get("title", topic).strip()
        content = parsed.get("content", summary or topic).strip()
        post_type = parsed.get("type", "Creative").strip()

    except Exception as e:
        print("⚠️ Failed to parse GPT response:", e)
        title = topic
        content = summary or topic
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
