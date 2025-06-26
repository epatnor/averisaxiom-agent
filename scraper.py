# scraper.py

import requests
import feedparser
import os

# === GOOGLE NEWS ===
def fetch_google_news():
    """
    Hämtar relevanta nyheter från Google News RSS-feed.
    Filtrerar bort sport, kändisar, underhållning etc.
    Behåller bara nyheter om politik, teknik, AI och vetenskap.
    """
    print("🔍 Fetching Google News RSS...")

    # Lista över godkända nyckelord
    relevant_keywords = [
        "world", "politics", "election", "president", "government",
        "tech", "technology", "AI", "artificial intelligence",
        "science", "research", "space", "innovation"
    ]

    feed_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(feed_url)
    results = []

    for entry in feed.entries:
        title_lower = entry.title.lower()
        # Behåll bara nyheter som innehåller något relevant nyckelord
        if any(keyword in title_lower for keyword in relevant_keywords):
            results.append({
                "title": entry.title,
                "type": "auto",
                "source": "Google News"
            })

    print(f"✅ Retained {len(results)} relevant headlines from Google News.")
    return results


# === YOUTUBE VIDEOS ===
def fetch_youtube_videos():
    """
    Hämtar YouTube-videotitlar baserat på flera relevanta teman.
    Kräver en miljövariabel: YOUTUBE_API_KEY.
    """
    print("🔍 Fetching YouTube videos...")
    API_KEY = os.getenv("YOUTUBE_API_KEY")

    if not API_KEY:
        print("⚠️ WARNING: No YOUTUBE_API_KEY found.")
        return []

    # Fokusfrågor för olika ämnesområden
    queries = [
        "world politics",
        "american elections",
        "AI breakthroughs",
        "tech news",
        "space exploration",
        "scientific discoveries"
    ]

    results = []

    for query in queries:
        url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&q={query}&type=video&maxResults=5&key={API_KEY}"
        )
        try:
            response = requests.get(url)
            data = response.json()
            for item in data.get("items", []):
                title = item['snippet']['title']
                results.append({
                    "title": title,
                    "type": "auto",
                    "source": "YouTube"
                })
        except Exception as e:
            print(f"❌ Error fetching YouTube query '{query}': {e}")

    print(f"✅ Retrieved {len(results)} relevant YouTube titles.")
    return results
