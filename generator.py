# generator.py

import os
import openai
import json
from dotenv import load_dotenv
from utils import remove_emojis_and_codeblock

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_post(topic, summary, style=None):
    """Generates a post based on a topic/summary, with an auto-detected type and improved title."""

    print(f"Generating post for: {topic} [style: {style}]")

    # English prompt for international usage with clearer title instruction
    system_prompt = (
        "You are a professional social media assistant.\n"
        "Given a topic and/or summary, generate a short, intelligent post for an educated audience.\n"
        "Avoid emojis, hashtags, clickbait, or slang.\n"
        "Keep tone factual, neutral, and slightly journalistic.\n"
        "Write a distinct, relevant title that summarizes the idea clearly.\n"
        "Return ONLY valid JSON in this format:\n"
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
