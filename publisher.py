# === File: publisher.py ===
from atproto import Client
from config import Config
import db

def publish_to_bluesky(post_id, content):
    if Config.TEST_MODE:
        print(f"[TEST MODE] Would publish post {post_id}: {content}")
        db.mark_as_published(post_id, bluesky_uri="test-uri")
        return

    client = Client()
    client.login(Config.BLUESKY_HANDLE, Config.BLUESKY_APP_PASSWORD)
    try:
        response = client.send_post(content)
        bluesky_uri = response.uri
        db.mark_as_published(post_id, bluesky_uri)
        print(f"Published post {post_id} to Bluesky, URI: {bluesky_uri}")
    except Exception as e:
        print(f"Failed to publish post {post_id}: {e}")
