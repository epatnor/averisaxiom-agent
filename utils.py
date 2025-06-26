# utils.py

import re

def remove_emojis_and_codeblock(text):
    """
    Tar bort emojis och markdown-block (t.ex. ```json) från GPT-svar.
    Returnerar en renad sträng.
    """
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).strip("` \n")
    text = re.sub(r"[^\w\s.,;:!?\"'()\[\]{}<>/@\-–—=+%€$£&|#*]", "", text)
    return text.strip()
