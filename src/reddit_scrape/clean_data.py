import pandas as pd
import html
import re
import unicodedata
import ast

# =========================
# TEXT CLEANING FUNCTION
# =========================
def clean_text(text):
    if not isinstance(text, str):
        return ""

    # Remove if just '[removed]' or '[deleted]'
    if text.strip().lower() in ["[removed]", "[deleted]"]:
        return ""

    # Decode HTML entities like &gt;, &amp;
    text = html.unescape(text)

    # Normalize Unicode and remove invisible characters
    text = unicodedata.normalize("NFKC", text)
    text = text.replace('\xa0', ' ').replace('\u200b', '')

    # Remove escape sequences and fix quotes
    text = text.replace('\\n', ' ').replace('\\r', ' ').replace('\\t', ' ')
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    text = text.replace("\\'", "'").replace('\\"', '"')

    # Fix curly punctuation and other odd symbols
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('‘', "'").replace('’', "'")
    text = text.replace('…', '...').replace('–', '-').replace('—', '-')
    text = text.replace('«', '"').replace('»', '"')

    # Remove markdown (preserve URLs)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)     # bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)         # italic
    text = re.sub(r'~~(.*?)~~', r'\1', text)         # strikethrough
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)      # remove embedded media

    # Remove any embedded '[removed]' or '[deleted]'
    text = re.sub(r'\[removed\]|\[deleted\]', '', text, flags=re.IGNORECASE)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# =========================
# COMMENTS PARSER + CLEANER
# =========================
def parse_comments(comment_str):
    try:
        return ast.literal_eval(comment_str)
    except:
        return []

def clean_comments(comment_list):
    return [(clean_text(text), score) for (text, score) in comment_list if clean_text(text)]

# =========================
# MAIN PIPELINE
# =========================
def clean_dogecoin_data(input_file: str, output_file: str):
    df = pd.read_csv(input_file)

    # Drop empty 'url' column if present
    if 'url' in df.columns:
        df.drop(columns=["url"], inplace=True)

    # Handle NaNs
    df["selftext"] = df["selftext"].fillna("")
    df["flair"] = df["flair"].fillna("None")

    # Parse and clean comments
    df["comments"] = df["comments"].apply(parse_comments)
    df["comments"] = df["comments"].apply(clean_comments)

    # Clean title and selftext
    df["title"] = df["title"].apply(clean_text)
    df["selftext"] = df["selftext"].apply(clean_text)

    # Combine to full_text
    df["full_text"] = (df["title"] + " " + df["selftext"]).str.strip()

    # Save to file
    df.to_csv(output_file, index=False)
    print(f"✅ Cleaned file saved to: {output_file}")

# =========================
# RUN CLEANING
# =========================
if __name__ == "__main__":
    input_csv = "pepe_final.csv"  # Replace with your actual input file path
    output_csv = "pepe_full_cleaned_final.csv"
    clean_dogecoin_data(input_csv, output_csv)
