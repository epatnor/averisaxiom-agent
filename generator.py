# === File: generator.py ===

import openai
from config import Config

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

    system_prompts = {
        "news": "You are AverisAxiom, a neutral, factual social media assistant. Write a short, objective, news-style post based on the following topic.",
        "thoughts": "You are AverisAxiom, a thoughtful assistant reflecting on topics with personal insight. Write a short, reflective post adding some personal perspective to the following topic.",
        "questions": "You are AverisAxiom, an engaging assistant. Write a short post presenting this topic and invite readers to share their opinions or experiences.",
        "raw": "You are AverisAxiom, fully free to expand on the following idea without filters. Keep an expressive, edgy, unfiltered tone that reflects the prompt directly."
    }

    system_prompt = system_prompts.get(mood, system_prompts["news"])  # fallback to news

    client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500,
        n=1
    )

    content = response.choices[0].message.content.strip()
    return content
