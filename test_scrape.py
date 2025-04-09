import requests
import csv
from datetime import datetime
import time

# Config
query = "doge OR dogecoin"
subreddit = "CryptoCurrency"
start_time = int(datetime(2023, 4, 17).timestamp())
end_time = int(datetime(2023, 4, 19).timestamp())
size = 100  # max 1000 if needed
sleep_time = 1  # avoid rate limit

filename = "doge_scroll_redditsearchio.csv"
with open(filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Author", "Upvotes", "Date", "URL"])

    current_time = start_time
    total = 0

    while current_time < end_time:
        print(f"🔍 Fetching posts after {datetime.utcfromtimestamp(current_time)}...")
        url = "https://api.redditsearch.io/search"
        params = {
            "query": query,
            "subreddit": subreddit,
            "after": current_time,
            "before": end_time,
            "size": size,
            "sort": "asc"
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print("❌ Error:", response.status_code, response.text)
            break

        posts = response.json().get("posts", [])
        if not posts:
            print("✅ No more posts in range.")
            break

        for post in posts:
            created = post["created_utc"]
            current_time = max(current_time, created + 1)  # advance
            writer.writerow([
                post.get("title", ""),
                post.get("author", ""),
                post.get("score", 0),
                datetime.utcfromtimestamp(created).strftime("%Y-%m-%d %H:%M:%S"),
                f"https://reddit.com{post.get('permalink', '')}"
            ])
            print(f"✅ {post.get('title', '')[:60]}...")

        total += len(posts)
        time.sleep(sleep_time)

print(f"\n🎉 Done! Total posts saved: {total}")
