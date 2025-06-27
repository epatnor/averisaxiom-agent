import sqlite3
import os

SETTINGS_DB = "settings.db"

def init_settings_db():
    """Create the settings.db with a settings table if it doesn't exist."""
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


def get_setting(key):
    """Retrieve a setting value by key."""
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def set_setting(key, value):
    """Insert or update a setting key/value pair."""
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, value))
    conn.commit()
    conn.close()


def get_all_settings():
    """Return a dictionary of all settings."""
    conn = sqlite3.connect(SETTINGS_DB)
    c = conn.cursor()
    c.execute("SELECT key, value FROM settings")
    rows = c.fetchall()
    conn.close()
    return {key: value for key, value in rows}
