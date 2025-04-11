import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from tqdm import tqdm

# Step 1: Load dataset
df = pd.read_csv('data/dogecoin/dogecoin_full_cleaned_final.csv')
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

# Step 4: Apply FinBERT with sliding window
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

# Step 5: Save results
df.to_csv('finbert_vader_sentiment_results.csv', index=False)
print("✅ Analysis complete. Raw VADER and FinBERT sentiment saved to 'finbert_vader_sentiment_results.csv'")
