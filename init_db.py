import sqlite3

DB_PATH = "./data/posts.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT UNIQUE,
            status TEXT,
            like_count INTEGER DEFAULT 0,
            repost_count INTEGER DEFAULT 0,
            reply_count INTEGER DEFAULT 0,
            content TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
