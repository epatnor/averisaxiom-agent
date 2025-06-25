
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def cluster_and_summarize(headlines):
    system_prompt = "Cluster these headlines into 5 storylines and summarize each storyline."
    joined = "\n".join(headlines)

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": joined}
        ]
    )

    text = response.choices[0].message.content
    clusters = []
    for line in text.split("\n"):
        if line.strip():
            parts = line.split(":", 1)
            if len(parts) == 2:
                clusters.append({"title": parts[0].strip(), "summary": parts[1].strip()})
    return clusters
