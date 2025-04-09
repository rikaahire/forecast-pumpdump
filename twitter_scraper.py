import snscrape.modules.twitter as sntwitter
import pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# === CONFIG ===
query = "dogecoin OR #dogecoin OR #doge OR $DOGE since:2023-04-01 until:2023-04-03 lang:en"
like_threshold = 20
limit = 1000  # Total tweets to scrape

tweets = []
analyzer = SentimentIntensityAnalyzer()

# === SCRAPE ===
print("🔍 Starting scrape...")

for tweet in sntwitter.TwitterSearchScraper(query).get_items():
    if len(tweets) >= limit:
        break

    if tweet.likeCount < like_threshold:
        continue

    sentiment = analyzer.polarity_scores(tweet.content)['compound']
    hour = tweet.date.replace(minute=0, second=0, microsecond=0)

    tweets.append([
        tweet.date,
        hour.strftime('%Y-%m-%d %H:00'),
        tweet.user.username,
        tweet.likeCount,
        tweet.content,
        sentiment,
        tweet.url
    ])

print(f"✅ Collected {len(tweets)} tweets.")

# === SAVE FULL TWEET DATA ===
df = pd.DataFrame(tweets, columns=["datetime", "hour", "user", "likes", "content", "sentiment", "url"])
df.to_csv("doge_tweets.csv", index=False)
print("📁 Saved: doge_tweets.csv")

# === AGGREGATE BY HOUR ===
hourly = df.groupby("hour").agg(
    tweet_count=("sentiment", "count"),
    avg_sentiment=("sentiment", "mean"),
    sentiment_std=("sentiment", "std")
).reset_index()

hourly.to_csv("doge_hourly_sentiment.csv", index=False)
print("📁 Saved: doge_hourly_sentiment.csv")
