# === File: generator.py ===

import openai
from config import Config
from db import get_setting

def autodetect_mood(prompt):
    client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

    system_prompt = (
        "You are a content assistant. Based on the user's input, select the most suitable post style. "
        "Your options are strictly: news, thoughts, questions, or raw. "
        "Respond with only one of these words."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Prompt: {prompt}"}
        ],
        temperature=0,
        max_tokens=5,
        n=1
    )

    mood = response.choices[0].message.content.strip().lower()
    if mood not in ["news", "thoughts", "questions", "raw"]:
        mood = "news"  # fallback default
    return mood

def generate_post(prompt, dry_run=False, mood="news"):
    if dry_run:
        return "[DRY RUN] Generated post would appear here."

    # Load base prompt from settings or use default
    def_prompt = (
        "You are AverisAxiom, a calm, clear, reflective AI assistant helping craft short, thoughtful, friendly social media posts "
        "for a well-educated but general audience. Avoid hype, slang, or overly casual language. Keep a professional, respectful tone."
    )
    base_prompt = get_setting("system_prompt", def_prompt)

    mood_prompts = {
        "news": "Write a short, neutral, objective, news-style post based on the following topic. Limit to 3-5 sentences.",
        "thoughts": "Write a short, reflective post adding some personal perspective to the following topic. Limit to 3-5 sentences.",
        "questions": "Write a short post presenting this topic and invite readers to share their opinions or experiences. Limit to 3-5 sentences.",
        "raw": "Expand freely on the following idea without filters. Keep an expressive, edgy, unfiltered tone. Limit to 3-5 sentences."
    }

    mood_prompt = mood_prompts.get(mood, mood_prompts["news"])

    full_system_prompt = f"{base_prompt}\n\n{mood_prompt}"

    client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=250,
        n=1
    )

    content = response.choices[0].message.content.strip()
    return content
