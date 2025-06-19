# === File: publisher.py ===
from atproto import Client
from config import Config
import db

client = Client()
client.login(Config.BLUESKY_HANDLE, Config.BLUESKY_APP_PASSWORD)

def publish_to_bluesky():
    pending_posts = db.get_pending_posts()
    for post in pending_posts:
        post_id, prompt, content = post
        try:
            client.send_post(content)
            db.mark_as_published(post_id)
            print(f"Published post {post_id} to Bluesky")
        except Exception as e:
            print(f"Failed to publish post {post_id}: {e}")