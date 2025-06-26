# === File: generator.py ===

import os
import openai

from dotenv import load_dotenv
load_dotenv()


client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_post(title, summary, style="News"):
    print(f"Generating post for: {title} [{style}]")

    system_prompt = (
        "You are a professional social media writer. Based on the title and summary, "
        "write a short engaging post suitable for Twitter or Bluesky. "
        "Do NOT include hashtags. Keep it concise and impactful."
    )

    user_prompt = f"Title: {title}\nSummary: {summary}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.5
    )

    text = response.choices[0].message.content.strip()

    return {
        "title": title,
        "summary": text,  # <-- spara GPT-texten i summary-fältet
        "status": "draft",
        "type": style.lower(),
        "comments": 0,
        "likes": 0,
        "shares": 0
    }

