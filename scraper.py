
import requests, feedparser, os

def fetch_google_news():
    url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    return [{"title": e.title, "type": "auto", "source": "Google News"} for e in feed.entries]

def fetch_youtube_videos(query="world news"):
    api_key = os.getenv("YOUTUBE_API_KEY")
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=10&key={api_key}"
    resp = requests.get(url).json()
    return [{"title": i['snippet']['title'], "type": "auto", "source": "YouTube"} for i in resp.get("items", [])]
