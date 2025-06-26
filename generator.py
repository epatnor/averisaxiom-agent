# generator.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from utils import remove_emojis_and_codeblock

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Generates a social media post from a story dict (title + summary)
def generate_post(story):
    prompt = (
        "Write a short-form post based on the following topic.\n"
        "It should feel like a thoughtful, relevant observation or commentary.\n"
        "Use a neutral but refined tone. No hashtags, no emojis, no questions.\n"
        "Keep it around 300–400 characters – slightly longer than a tweet, but still concise.\n\n"
        f"Topic: {story['title']}\n"
        f"Summary: {story['summary']}\n\n"
        "Post:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                { "role": "system", "content": "Always reply with plain English text. No code blocks, no emojis." },
                { "role": "user", "content": prompt }
            ],
            temperature=0.7
        )
        raw = response.choices[0].message.content.strip()
        text = remove_emojis_and_codeblock(raw)
        return text

    except Exception as e:
        print("⚠️ Failed to generate post:", e)
        return None

# Generates a more specific, headline-style title
def generate_better_title(story):
    prompt = (
        "You are an assistant that writes short, specific titles for social media posts.\n"
        "The title should sound like a news headline or teaser. Avoid generic phrases like 'AI news' or 'Global politics'.\n"
        "Keep it under 10 words, and make it catchy but relevant.\n\n"
        f"Post content: {story['summary']}\n\n"
        "Title:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                { "role": "system", "content": "Reply with a single short title in English. No emojis." },
                { "role": "user", "content": prompt }
            ],
            temperature=0.6
        )
        title = remove_emojis_and_codeblock(response.choices[0].message.content.strip())

        if len(title.split()) < 3 or any(generic in title.lower() for generic in ["politics", "technology", "ai", "news", "update"]):
            title = story['summary'][:60].rstrip('.') + "…"

        return title

    except Exception as e:
        print("⚠️ Failed to generate title:", e)
        return story['summary'][:60].rstrip('.') + "…"

# Generates both a better title and a post text from a story
def generate_full_post(story):
    title = generate_better_title(story)
    body = generate_post(story)
    return {
        "title": title,
        "summary": body
    }
