# settings_db.py

import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Path to SQLite settings database
SETTINGS_DB = "settings.db"

# List of expected keys (used for .env fallback)
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

# --- Init ---

def init_settings_db():
    """Creates the settings database and table if it doesn't exist."""
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


# --- Get / Set Single ---

def get_setting(key):
    """
    Retrieve a single setting from the database.
    Falls back to .env if not found or empty.
    """
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()

    if row and row[0] not in [None, ""]:
        return row[0]
    return os.getenv(key, "")


def set_setting(key, value):
    """
    Set or update a single setting in the database.
    """
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, value))
    conn.commit()
    conn.close()


# --- Get All ---

def get_all_settings():
    """
    Load all settings from the database.
    Falls back to .env values for any expected keys not found in the DB.
    """
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

    # Add missing expected keys from .env as fallback
    for key in EXPECTED_KEYS:
        if key not in settings or settings[key] in [None, ""]:
            settings[key] = os.getenv(key, "")

    return settings


# --- Optional Utility ---

def get_setting_with_fallback(key, fallback_env):
    """
    Fetch a setting using one key, but fallback to another .env key if missing.
    """
    value = get_setting(key)
    if value not in [None, ""]:
        return value
    return os.getenv(fallback_env, "")
