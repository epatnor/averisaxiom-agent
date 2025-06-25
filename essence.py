# === File: essence.py ===

import openai
import os
import json

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def cluster_and_summarize(headlines):
    print("Running AI clustering & summarization...")

    prompt = f"""
You are an AI news clustering assistant.

You will receive a list of headlines. Your task is to group them into logical clusters based on common topics, then write a brief summary for each cluster. Return only valid JSON array of objects, where each object has:

- title: A short representative title for the cluster.
- summary: A 2-3 sentence summary of the topic.

Here are the headlines:

{headlines}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a news summarization assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        raw_output = response.choices[0].message.content
        print("Raw AI output:", raw_output)

        # Try to load JSON directly from response
        clusters = json.loads(raw_output)
        return clusters

    except json.JSONDecodeError as e:
        print("Error parsing AI response:", e)
        return []

    except Exception as e:
        print("Unexpected error from OpenAI:", e)
        return []
