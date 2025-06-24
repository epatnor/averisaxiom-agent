# === File: scraper.py ===

import requests
import feedparser
import os

def fetch_google_news():
    print("Fetching Google News RSS...")
    feed_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(feed_url)
    results = []
    for entry in feed.entries:
        results.append({
            "title": entry.title,
            "type": "auto",
            "source": "Google News"
        })
    return results

def fetch_youtube_videos(query="world news"):
    print("Fetching YouTube videos...")
    API_KEY = os.getenv("YOUTUBE_API_KEY")
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=10&key={API_KEY}"
    resp = requests.get(search_url)
    data = resp.json()

    results = []
    for item in data.get("items", []):
        title = item['snippet']['title']
        results.append({
            "title": title,
            "type": "auto",
            "source": "YouTube"
        })
    return results
