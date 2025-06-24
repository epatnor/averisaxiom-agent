# === File: essence.py ===

import openai
import json
from config import Config

openai.api_key = Config.OPENAI_API_KEY

def cluster_and_summarize(headlines):
    print("Running AI clustering & summarization...")

    prompt = f"""
You are an expert news analyst. Given the following list of headlines, group them into major storylines and summarize each storyline concisely.

Return the output strictly as a JSON list where each item contains:

- "title": a very short title for the storyline (max 10 words)
- "summary": a 2-3 sentence summary of that storyline

Headlines:
{headlines}

Output:
"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a news clustering and summarization expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    raw_output = response.choices[0].message.content.strip()

    # Try to extract JSON even if GPT adds extra text
    try:
        first_brace = raw_output.find('[')
        last_brace = raw_output.rfind(']')
        json_str = raw_output[first_brace:last_brace+1]
        parsed = json.loads(json_str)
    except Exception as e:
        print("Failed to parse GPT output:", e)
        print("Raw GPT output was:\n", raw_output)
        raise e

    print(f"Condensed into {len(parsed)} major storylines")
    return parsed
