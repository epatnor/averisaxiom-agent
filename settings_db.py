# settings_db.py

import sqlite3
import os
from dotenv import load_dotenv

SETTINGS_DB = "settings.db"
load_dotenv()  # Load values from .env at startup


# Create the settings.db if it doesn't exist
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


# Get one specific setting by key, or fallback to .env if not found or empty
def get_setting(key):
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()

    if row and row[0] not in [None, ""]:
        return row[0]
    return os.getenv(key, "")


# Set or update a single setting
def set_setting(key, value):
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, value))
    conn.commit()
    conn.close()


# Load all settings as a dictionary, including fallback values from .env
def get_all_settings():
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("SELECT key, value FROM settings")
    rows = c.fetchall()
    conn.close()

    settings = {key: value for key, value in rows}

    # Add fallback env vars if not already set in db
    for key, val in os.environ.items():
        if key not in settings or settings[key] in [None, ""]:
            settings[key] = val

    return settings


# (Optional) Separate fallback method, if you want to force using a specific env key
def get_setting_with_fallback(key, fallback_env):
    value = get_setting(key)
    if value not in [None, ""]:
        return value
    return os.getenv(fallback_env, "")
