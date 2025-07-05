# settings_db.py

import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Path to the SQLite settings database
SETTINGS_DB = "settings.db"

# List of expected keys (used for .env fallback and UI population)
EXPECTED_KEYS = [
    "OPENAI_API_KEY", "SERPER_API_KEY",
    "MASTODON_BASE_URL", "MASTODON_ACCESS_TOKEN",
    "BLUESKY_HANDLE", "BLUESKY_APP_PASSWORD",
    "YOUTUBE_API_KEY", "TEST_MODE",
    "GOOGLE_RSS_URL", "GOOGLE_MAX_AGE", "GOOGLE_MAX_ITEMS",
    "GOOGLE_QUERY", "GOOGLE_REQUIRE_DATE", "GOOGLE_DESCRIPTION",
    "YOUTUBE_FEED_URL", "YOUTUBE_DESCRIPTION",
    "USE_X", "USE_BLUESKY", "USE_MASTODON"
]

# Substrings that indicate a value is a dummy placeholder
DUMMY_MARKERS = [
    "your-openai-key-here", "example.com", "proxy.example",
    "bluesky-app-password-here", "mastodon-access-token-here",
    "youtube-api-key-here", "serper-api-key-here", "bsky.social"
]

# Create the settings table if it doesn't exist
def init_settings_db():
    if not os.path.exists(SETTINGS_DB):
        print("==> Creating settings.db...")
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

# Detect if a setting value is empty or clearly a placeholder
def is_dummy(value: str) -> bool:
    if not value or value.strip() == "":
        return True
    return any(marker in value for marker in DUMMY_MARKERS)

# Retrieve a single setting from the database or fall back to .env
def get_setting(key: str) -> str:
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()

    if row and row[0] not in [None, ""]:
        return row[0]
    return os.getenv(key, "")

# Insert or update a single setting in the database
def set_setting(key: str, value: str) -> None:
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, value))
    conn.commit()
    conn.close()

# Load all settings from the database with .env fallback
def get_all_settings() -> dict:
    settings = {}

    try:
        conn = sqlite3.connect(SETTINGS_DB)
        c = conn.cursor()
        c.execute("SELECT key, value FROM settings")
        rows = c.fetchall()
        conn.close()
        settings = {key: value for key, value in rows if value not in [None, ""]}
    except Exception as e:
        print(f"⚠️ Failed to load settings from DB: {e}")

    # Fill in any missing expected keys using .env
    for key in EXPECTED_KEYS:
        if key not in settings or settings[key] in [None, ""]:
            settings[key] = os.getenv(key, "")

    # Log any dummy values found in the settings
    for key, val in settings.items():
        if is_dummy(val):
            print(f"⚠️ Dummy value detected for '{key}'")

    return settings

# Fetch a setting using one key, or fallback to another .env key
def get_setting_with_fallback(key: str, fallback_env: str) -> str:
    value = get_setting(key)
    if value not in [None, ""]:
        return value
    return os.getenv(fallback_env, "")
