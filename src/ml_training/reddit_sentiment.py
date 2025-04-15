import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from tqdm import tqdm
import ast
from collections import Counter

# Step 1: Load dataset
df = pd.read_csv('data/reddit_posts/preprocessed_post/shiba_wo_emoji.csv')
df = df[df['full_text'].notna() & (df['full_text'].str.strip() != '')].copy()

# Step 2: VADER setup
nltk.download('vader_lexicon')
vader = SentimentIntensityAnalyzer()
df['vader_sentiment'] = df['full_text'].apply(lambda text: vader.polarity_scores(str(text))['compound'])

# Step 3: FinBERT setup (sliding window)
tokenizer = BertTokenizer.from_pretrained('ProsusAI/finbert')
model = BertForSequenceClassification.from_pretrained('ProsusAI/finbert')
label_map = {0: 'positive', 1: 'negative', 2: 'neutral'}

def chunk_text_to_window_size_and_predict_proba(input_ids, attention_mask, total_len):
    proba_list = []
    start = 0
    window_length = 510
    loop = True

    while loop:
        end = start + window_length
        if end >= total_len:
            loop = False
            end = total_len

        input_ids_chunk = input_ids[start:end]
        attention_mask_chunk = attention_mask[start:end]

        input_ids_chunk = [101] + input_ids_chunk + [102]
        attention_mask_chunk = [1] + attention_mask_chunk + [1]

        input_dict = {
            'input_ids': torch.tensor([input_ids_chunk]).long(),
            'attention_mask': torch.tensor([attention_mask_chunk]).int()
        }

        with torch.no_grad():
            outputs = model(**input_dict)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            proba_list.append(probabilities)

        start = end

    return proba_list

def get_mean_from_proba(proba_list):
    with torch.no_grad():
        stacks = torch.stack(proba_list)
        stacks = stacks.view(stacks.shape[0], stacks.shape[2])
        mean = stacks.mean(dim=0)
    return mean

# Step 4: Apply FinBERT with sliding window to post content
print("Running FinBERT sliding window sentiment analysis...")
predictions = []

for text in tqdm(df['full_text']):
    tokens = tokenizer.encode_plus(text, add_special_tokens=False)
    input_ids = tokens['input_ids']
    attention_mask = tokens['attention_mask']
    total_len = len(input_ids)

    proba_list = chunk_text_to_window_size_and_predict_proba(input_ids, attention_mask, total_len)
    mean = get_mean_from_proba(proba_list)
    sentiment_idx = torch.argmax(mean).item()
    sentiment_label = label_map[sentiment_idx]
    predictions.append(sentiment_label)

df['finbert_sliding_sentiment'] = predictions

# Step 5: Add average VADER and FinBERT sentiment for comments
def analyze_comments(comment_str, index=None):
    if index is not None and index % 100 == 0:
        print(f"[{index}] ✅ Finished comment sentiment analysis for post {index}")

    if pd.isna(comment_str) or comment_str.strip() == "":
        return 0.0, "neutral"

    try:
        comments = ast.literal_eval(comment_str)
        if not isinstance(comments, list):
            comments = [str(comments)]
    except:
        comments = [comment_str]

    # Filter and sort top 10 by vote count
    valid_comments = [c for c in comments if isinstance(c, tuple) and len(c) == 2 and isinstance(c[1], (int, float))]
    top_comments = sorted(valid_comments, key=lambda x: x[1], reverse=True)[:10]

    vader_scores = []
    finbert_labels = []

    for i, (comment_text, vote) in enumerate(top_comments):
        # VADER
        vader_score = vader.polarity_scores(str(comment_text))['compound']
        vader_scores.append(vader_score)

        # FinBERT
        tokens = tokenizer.encode_plus(comment_text, add_special_tokens=False)
        input_ids = tokens['input_ids']
        attention_mask = tokens['attention_mask']
        total_len = len(input_ids)

        if total_len == 0:
            continue

        proba_list = chunk_text_to_window_size_and_predict_proba(input_ids, attention_mask, total_len)
        mean = get_mean_from_proba(proba_list)
        sentiment_idx = torch.argmax(mean).item()
        sentiment_label = label_map[sentiment_idx]
        finbert_labels.append(sentiment_label)

    avg_vader = sum(vader_scores) / len(vader_scores) if vader_scores else 0.0

    if finbert_labels:
        most_common_label = Counter(finbert_labels).most_common(1)[0][0]
    else:
        most_common_label = "neutral"

    return avg_vader, most_common_label


print("Analyzing comments...")
comment_results = df['comments'].apply(analyze_comments)
df['avg_vader_comments'] = comment_results.apply(lambda x: x[0])
df['avg_finbert_comments'] = comment_results.apply(lambda x: x[1])

# Step 6: Save results
df.to_csv('shiba_sentiment_wo_emoji.csv', index=False)
print("✅ Analysis complete. Post + comment sentiment saved to 'finbert_vader_sentiment_results.csv'")
