# === File: essence.py (nu med summary) ===

from openai import OpenAI
from config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

def cluster_and_summarize(headlines: list) -> list:
    """
    Takes a list of headlines, asks GPT-4o to extract major storylines, cluster them,
    and produce both a title and short summary for each storyline.
    """
    system_prompt = (
        "You are a professional news editor. Given a list of news headlines, "
        "cluster them into 3-5 main storylines. For each storyline, output:\n"
        "- A short title summarizing the topic\n"
        "- A short 2-3 sentence summary of the storyline\n\n"
        "Format exactly as:\n\n"
        "Title: ...\nSummary: ...\n\n"
        "Be concise and avoid redundancy."
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

    output = response.choices[0].message.content
    storylines = []

    for block in output.strip().split("\n\n"):
        lines = block.strip().split("\n")
        title_line = next((l for l in lines if l.startswith("Title: ")), None)
        summary_line = next((l for l in lines if l.startswith("Summary: ")), None)
        if title_line and summary_line:
            storylines.append({
                "title": title_line.replace("Title: ", "").strip(),
                "summary": summary_line.replace("Summary: ", "").strip()
            })

    return storylines
