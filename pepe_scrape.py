import requests
import pandas as pd
import datetime
import time

# Configuration for Pepe scraping
COIN_QUERY = "pepe OR pepe coin"
SUBREDDITS = ["Pepecryptocurrency", "CryptoCurrency", "Memecoins"]
OUTPUT_FILE = "pepe_posts.csv"

# API endpoints
SUBMISSION_URL = "https://api.pullpush.io/reddit/search/submission/"
COMMENT_URL = "https://api.pullpush.io/reddit/search/comment/"

def fetch_posts(start_date, end_date):
    """Fetch posts from Reddit API within the specified date range."""
    all_posts = []
    current_date = start_date

    while current_date <= end_date:
        after_ts = int(datetime.datetime.combine(current_date, datetime.time.min).timestamp())
        before_ts = int(datetime.datetime.combine(current_date, datetime.time.max).timestamp())

        for subreddit in SUBREDDITS:
            params = {
                "q": COIN_QUERY,
                "subreddit": subreddit,
                "after": after_ts,
                "before": before_ts,
                "size": 100,
                "sort": "asc"
            }

            try:
                response = requests.get(SUBMISSION_URL, params=params)
                print(f"📅 {current_date}: {response.status_code} - r/{subreddit}")
                
                if response.status_code == 200:
                    for post in response.json().get("data", []):
                        post_data = {
                            "title": post.get("title"),
                            "selftext": post.get("selftext"),
                            "score": post.get("score"),
                            "num_comments": post.get("num_comments"),
                            "created_utc": datetime.datetime.utcfromtimestamp(post.get("created_utc")),
                            "url": post.get("full_link"),
                            "subreddit": subreddit,
                            "flair": post.get("link_flair_text")
                        }
                        all_posts.append(post_data)
                        time.sleep(0.3)  # Be polite to the API

            except Exception as e:
                print(f"⚠️ Error fetching posts for r/{subreddit}: {e}")

        current_date += datetime.timedelta(days=1)
        time.sleep(1)

    return pd.DataFrame(all_posts)

if __name__ == "__main__":
    start_date = datetime.date(2023, 4, 15)
    end_date = datetime.date(2023, 6, 30)

    print(f"🚀 Starting Pepe scraping from {start_date} to {end_date}...")
    df = fetch_posts(start_date, end_date)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Saved {len(df)} posts to {OUTPUT_FILE}")