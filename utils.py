# utils.py

import re

def remove_emojis_and_codeblock(text):
    """
    Tar bort emojis och markdown-block (t.ex. ```json) från GPT-svar.
    Returnerar en renad sträng.
    """
    # Ta bort markdown-codeblock-start ``` eller ```json etc.
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).strip("` \n")

    # Ta bort emojis (alla symboler som inte är vanliga tecken/punktuation)
    text = re.sub(r"[^
