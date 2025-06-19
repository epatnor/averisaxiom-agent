# === File: publisher.py ===
from atproto import Client
from config import Config
import db

client = Client()
client.login(Config.BLUESKY_HANDLE, Config.BLUESKY_APP_PASSWORD)

def publish_to_bluesky(post_id, content):
    try:
        client.send_post(content)
        db.mark_as_published(post_id)
        print(f"Published post {post_id} to Bluesky")
    except Exception as e:
        print(f"Failed to publish post {post_id}: {e}")
