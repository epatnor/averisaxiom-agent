
import requests
import feedparser
import os

def fetch_google_news():
    feed_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(feed_url)
    return [{"title": entry.title, "type": "auto", "source": "Google News"} for entry in feed.entries]

def fetch_youtube_videos(query="world news"):
    API_KEY = os.getenv("YOUTUBE_API_KEY")
    if not API_KEY:
        return []
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=10&key={API_KEY}"
    resp = requests.get(url)
    data = resp.json()
    return [{"title": item['snippet']['title'], "type": "auto", "source": "YouTube"} for item in data.get("items", [])]
