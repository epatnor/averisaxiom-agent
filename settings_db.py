# settings_db.py

import sqlite3
import os

SETTINGS_DB = "settings.db"

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

# Get one specific setting by key
def get_setting(key):
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

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

# Load all settings as a dictionary
def get_all_settings():
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("SELECT key, value FROM settings")
    rows = c.fetchall()
    conn.close()
    return {key: value for key, value in rows}

# Return a setting from db, or fallback to .env
def get_setting_with_fallback(key, fallback_env):
    value = get_setting(key)
    if value is not None:
        return value
    return os.getenv(fallback_env, "")
