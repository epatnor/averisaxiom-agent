# utils.py

import re

def remove_emojis_and_codeblock(text):
    """
    Tar bort emojis och markdown-kodblock (t.ex. ```json) från GPT-svar.
    Returnerar en renad sträng utan symboler, emojis eller formatteringstecken.
    """
    # Ta bort markdown-kodblock (``` eller ```json)
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).strip("` \n")

    # Ta bort icke-standardtecken (inkl. emojis och konstiga symboler)
    text = re.sub(
        r"[^\w\s.,;:!?\"'()\[\]{}<>/@\-–—=+%€$£&|#*]", "", 
        text, 
        flags=re.UNICODE
    )

    return text.strip()
