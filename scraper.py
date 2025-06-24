# scraper.py

import requests
import feedparser

# === YouTube Setup ===
YOUTUBE_API_KEY = "AIzaSyCRrGUbJasas6fI4SBI_UYpSXsWtD-ggAc"  # Lägg ev. i config senare
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

# === Google News RSS ===
GOOGLE_NEWS_RSS = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"


def fetch_google_news():
    print("Fetching Google News RSS...")
    feed = feedparser.parse(GOOGLE_NEWS_RSS)
    headlines = []
    for entry in feed.entries[:10]:
        headlines.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published
        })
    return headlines


def fetch_youtube_videos(query="world news"):
    print("Fetching YouTube videos...")
    params = {
        "part": "snippet",
        "type": "video",
        "q": query,
        "maxResults": 10,
        "order": "date",
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(YOUTUBE_SEARCH_URL, params=params)
    response.raise_for_status()
    data = response.json()

    videos = []
    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        videos.append({
            "title": snippet["title"],
            "videoId": video_id,
            "publishedAt": snippet["publishedAt"],
            "channelTitle": snippet["channelTitle"],
            "thumbnail": snippet["thumbnails"]["default"]["url"],
            "url": f"https://www.youtube.com/watch?v={video_id}"
        })
    return videos


if __name__ == "__main__":
    google_results = fetch_google_news()
    print("\nGoogle News Headlines:")
    for item in google_results:
        print(f"- {item['title']}")

    youtube_results = fetch_youtube_videos()
    print("\nYouTube Videos:")
    for item in youtube_results:
        print(f"- {item['title']} ({item['url']})")
