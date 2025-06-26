import os
import openai
import json
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_post(title, summary, style=None):
    print(f"Generating post for: {title} [auto-type detection]")

    system_prompt = (
        "You are a professional social media assistant.\n"
        "Your task is to generate a short, engaging post from a given topic or summary.\n"
        "You must also classify what type of post it is.\n\n"
        "Choose one of the following types:\n"
        "- News\n- Thought\n- Question\n- Satire\n- Creative\n- Raw\n- Rant\n- Joke\n\n"
        "Return only valid JSON in this format:\n"
        "{ \"content\": \"...\", \"type\": \"...\" }"
    )

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
