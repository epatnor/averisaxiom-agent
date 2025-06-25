
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_post(title, summary, style="News"):
    prompt = f"Write a {style} style social media post based on the following:\nTitle: {title}\nSummary: {summary}"
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You're a social media content generator."},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content
    return {"title": title, "summary": summary, "content": content, "style": style}
