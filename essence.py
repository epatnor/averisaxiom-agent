# === File: essence.py ===

import openai
import os
import json
import re

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_json_from_response(raw_output):
    """
    Attempts to safely extract JSON content even if OpenAI wraps it in markdown formatting.
    """
    try:
        # Look for json code block
        match = re.search(r"```json\s*(.*?)```", raw_output, re.DOTALL | re.IGNORECASE)
        if match:
            json_str = match.group(1).strip()
        else:
            # fallback: maybe it was not wrapped in ```
            json_str = raw_output.strip()

        return json.loads(json_str)
    except Exception as e:
        print("Error extracting JSON:", e)
        return []

def cluster_and_summarize(headlines):
    print("Running AI clustering & summarization...")

    prompt = f"""
You are an AI news clustering assistant.

You will receive a list of headlines. Your task is to group them into logical clusters based on common topics, then write a brief summary for each cluster. Return ONLY valid JSON array of objects, where each object has:

- title: A short representative title for the cluster.
- summary: A 2-3 sentence summary of the topic.

DO NOT include any explanation, just return pure JSON.

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

        clusters = extract_json_from_response(raw_output)
        return clusters

    except Exception as e:
        print("Unexpected error from OpenAI:", e)
        return []
