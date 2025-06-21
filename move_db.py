# === File: move_db.py ===

import os
import shutil

source = "/opt/render/project/src/posts.db"
target = "/mnt/data/posts.db"

if os.path.exists(source):
    shutil.move(source, target)
    print("Database file moved successfully.")
else:
    print("Source database file not found.")
