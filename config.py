# === File: config.py ===
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
    MASTODON_ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN", "")
    MASTODON_BASE_URL = os.getenv("MASTODON_BASE_URL", "https://mstdn.social")
    BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE", "averisaxiom.bsky.social")
    BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD", "5zh3-gqte-qubf-4qpx")

