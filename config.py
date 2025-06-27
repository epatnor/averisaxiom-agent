# === File: config.py ===

import os
from dotenv import load_dotenv

# Ladda in ev .env-filer
load_dotenv()

class Config:
    # Basdir korrekt oavsett var vi kör ifrån
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "posts.db")

    # API keys och credentials
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    MASTODON_ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")
    MASTODON_BASE_URL = os.getenv("MASTODON_BASE_URL")
    BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
    BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

    # Test mode
    TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

    # === Nya pipeline-inställningar (kommande från settings.html) ===
    MAX_NEWS_AGE_DAYS = int(os.getenv("MAX_NEWS_AGE_DAYS", 2))  # ex. 2 dagar gammal max
    MAX_NEWS_ITEMS = int(os.getenv("MAX_NEWS_ITEMS", 10))       # hämta max 10 nyheter
    NEWS_TOPICS = os.getenv("NEWS_TOPICS", "AI, klimat")        # ämnesfilter
    ONLY_WITH_PUBDATE = os.getenv("ONLY_WITH_PUBDATE", "true").lower() == "true"
