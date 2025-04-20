import requests
import pandas as pd
from tqdm import tqdm
import time
import re

# 🔐 Fireworks API Key (replace if needed)
API_KEY = "fw_3ZmpdjQQRaLK4ZEYqAYSvZzY"

# 📄 Input Reddit dataset
INPUT_CSV = "data/reddit_posts/preprocessed_post/shiba_wo_emoji.csv"
TEXT_COLUMN = "full_text"

# 🔗 Fireworks settings
API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
MODEL_NAME = "accounts/fireworks/models/llama4-scout-instruct-basic"

# 📥 Load and trim dataset
df = pd.read_csv(INPUT_CSV)
df = df[df[TEXT_COLUMN].notna() & (df[TEXT_COLUMN].str.strip() != "")].copy()

# 🧠 Improved prompt for FinBERT/VADER-style output
def classify_sentiment(text):
    prompt = (
        "You are a sentiment analysis model trained to mimic the behavior of FinBERT and VADER. "
        "You are analyzing Reddit posts about Shiba Inu (SHIB), which often contain slang, sarcasm, memes, or hype. "
        "Classify the sentiment of the following post as a real-valued score between -1 and 1, "
        "where -1 is strongly negative, 0 is neutral, and 1 is strongly positive. "
        "Base your decision on the tone and how the post would affect short-term Shiba Inu price movements. "
        "Return only the score (no label or explanation).\n\n"
        f"Post: \"{text}\""
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 10
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    for _ in range(3):  # Retry logic
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()

            # Extract numeric score, just in case extra text sneaks in
            match = re.search(r"-?\d+(\.\d+)?", content)
            return float(match.group(0)) if match else "error"

        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}... Retrying")
            time.sleep(1)

    return "error"

# 🌀 Run analysis
tqdm.pandas()
df['llm_sentiment_score'] = df[TEXT_COLUMN].progress_apply(classify_sentiment)

# 💾 Save results
OUTPUT_CSV = "shiba_sentiment_llama4.csv"
df.to_csv(OUTPUT_CSV, index=False)
print(f"✅ Done! Saved LLM sentiment results to: {OUTPUT_CSV}")
