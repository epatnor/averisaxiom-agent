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

# Substrings used to identify dummy placeholder values
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

# Return True if a value appears to be a dummy/placeholder
def is_dummy(value: str) -> bool:
    if not value or value.strip() == "":
        return True
    return any(marker in value for marker in DUMMY_MARKERS)

# Return a masked version of sensitive keys like API keys and tokens
def redact_sensitive(key: str, value: str) -> str:
    if any(s in key.upper() for s in ["KEY", "TOKEN", "PASSWORD"]):
        if value and len(value) > 10:
            return value[:4] + "..." + value[-4:]
        return "****"
    return value

# Retrieve a single setting from the database, or fall back to .env
def get_setting(key: str) -> str:
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    if row and row[0] not in [None, ""]:
        return row[0]
    return os.getenv(key, "")

# Insert or update a setting in the database
def set_setting(key: str, value: str) -> None:
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, value))
    conn.commit()
    conn.close()

# Load all settings from the database and supplement with .env if needed
# If include_metadata=True, also return a metadata dict with dummy/masked info
def get_all_settings(include_metadata=False) -> dict:
    settings = {}
    metadata = {}

    try:
        conn = sqlite3.connect(SETTINGS_DB)
        c = conn.cursor()
        c.execute("SELECT key, value FROM settings")
        rows = c.fetchall()
        conn.close()
        settings = {key: value for key, value in rows if value not in [None, ""]}
    except Exception as e:
        print(f"⚠️ Failed to load settings from DB: {e}")

    for key in EXPECTED_KEYS:
        if key not in settings or settings[key] in [None, ""]:
            settings[key] = os.getenv(key, "")

    if include_metadata:
        for key, val in settings.items():
            metadata[key] = {
                "is_dummy": is_dummy(val),
                "masked": redact_sensitive(key, val)
            }
        return settings, metadata

    return settings

# Retrieve a setting, falling back to an alternate env var if needed
def get_setting_with_fallback(key: str, fallback_env: str) -> str:
    value = get_setting(key)
    if value not in [None, ""]:
        return value
    return os.getenv(fallback_env, "")
