# === File: config.py ===

import os
from dotenv import load_dotenv

# Ladda in ev .env-filer (om vi har några)
load_dotenv()

class Config:
    # Basdir korrekt oavsett var vi kör ifrån
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "posts.db")

    # API keys och credentials (används när vi aktiverar respektive integration)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    MASTODON_ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")
    MASTODON_BASE_URL = os.getenv("MASTODON_BASE_URL")
    BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
    BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

    # Test mode flag (för framtida användning)
    TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
