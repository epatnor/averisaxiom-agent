# === File: essence.py (modern OpenAI SDK) ===

from openai import OpenAI
from config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

def cluster_and_summarize(headlines: list) -> list:
    """
    Takes a list of headlines, asks GPT-4o to extract main storylines and summarize them.
    """
    # Skapa input prompt
    system_prompt = (
        "You are an expert journalist and analyst. "
        "Given a list of raw news headlines, you will cluster similar stories together "
        "and generate 3-5 clear and concise storylines that summarize the major events. "
        "Be short, non-redundant, and focus on relevance."
    )

    user_prompt = "Here are today's headlines:\n\n" + "\n".join(f"- {h}" for h in headlines)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.5
    )

    # Extrahera resultatet
    output = response.choices[0].message.content

    # Enkelt: splitta på rad för varje storyline
    storylines = [line.strip("- ").strip() for line in output.split("\n") if line.strip()]
    return [{"title": s} for s in storylines]
