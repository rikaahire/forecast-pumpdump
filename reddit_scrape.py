import requests
import pandas as pd
import datetime
import time

# Start and end date for collection
start_date = datetime.date(2023, 4, 15)
end_date = datetime.date(2023, 6, 30)

# API endpoints
submission_url = "https://api.pullpush.io/reddit/search/submission/"
comment_url = "https://api.pullpush.io/reddit/search/comment/"

# Data collection
all_posts = []

# Loop over each day
current_date = start_date
while current_date <= end_date:
    after_ts = int(datetime.datetime.combine(current_date, datetime.time.min).timestamp())
    before_ts = int(datetime.datetime.combine(current_date, datetime.time.max).timestamp())

    params = {
        "q": "pepe",
        "subreddit": "CryptoCurrency",
        "after": after_ts,
        "before": before_ts,
        "size": 100,
        "sort": "asc"
    }

    response = requests.get(submission_url, params=params)
    print(f"📅 Fetching posts for {current_date} - Status code: {response.status_code}")

    if response.status_code == 200:
        posts = response.json().get("data", [])

        for post in posts:
            post_id = post.get("id")

            # Get top-level post fields
            post_data = {
                "title": post.get("title"),
                "selftext": post.get("selftext"),
                "score": post.get("score"),
                "num_comments": post.get("num_comments"),
                "created_utc": datetime.datetime.utcfromtimestamp(post.get("created_utc")),
                "url": post.get("full_link"),
                "subreddit": "CryptoCurrency",
                "flair": post.get("link_flair_text"),  # 👈 add this line
                "comments": []
            }

            # Fetch comments
            comment_params = {
                "link_id": post_id,
                "size": 100,
                "sort": "asc"
            }

            comment_response = requests.get(comment_url, params=comment_params)
            if comment_response.status_code == 200:
                comments = comment_response.json().get("data", [])
                post_data["comments"] = [
                    (c.get("body", ""), c.get("score", 0)) for c in comments
                ]
            else:
                print(f"❌ Failed to fetch comments for post {post_id}")

            all_posts.append(post_data)
            time.sleep(0.3)  # Be polite

    else:
        print("⚠️ Error:", response.text)

    current_date += datetime.timedelta(days=1)
    time.sleep(1)

# Convert to DataFrame
df = pd.DataFrame(all_posts)

# Save to CSV
df.to_csv("pepe_CryptoCurrency.csv", index=False)

print(f"\n✅ Done. Total posts: {len(df)}")
print(df.head())
