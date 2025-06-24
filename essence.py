# === essence.py ===

import openai
from config import Config

openai.api_key = Config.OPENAI_API_KEY

def cluster_and_summarize(headlines: list, max_groups: int = 5):
    """
    Take list of headlines, return grouped storylines with summaries.
    """

    headlines_text = "\n".join(f"- {h}" for h in headlines)

    system_prompt = (
        "You are an expert news analyst. "
        "Group these headlines into maximum {max_groups} key storylines. "
        "For each group, provide:\n"
        "1) A short 1-sentence title.\n"
        "2) A 1-2 sentence summary of the key situation.\n"
        "Focus on world news, technology, politics, economy, and science."
    ).format(max_groups=max_groups)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": headlines_text}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.5,
        max_tokens=1000
    )

    result = response.choices[0].message.content
    return parse_output(result)

def parse_output(output: str):
    """
    Very simple parser for GPT output. Assumes it returns numbered storylines.
    """

    storylines = []
    current = {}
    for line in output.splitlines():
        line = line.strip()
        if line.startswith(tuple("1234567890")) and '.' in line:
            if current:
                storylines.append(current)
                current = {}
            parts = line.split('.', 1)
            current['title'] = parts[1].strip()
        elif line:
            current['summary'] = line
    if current:
        storylines.append(current)
    return storylines
