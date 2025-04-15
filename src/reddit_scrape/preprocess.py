import pandas as pd
import re
import ast
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import emoji

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

def clean_text(text):

    text = str(text)

    # Lowercase
    text = text.lower().strip()

    # URLs
    text = re.sub(r'\bhttp\S*', '', text)

    # Mentions
    text = re.sub(r"@\w+", '', text)

    # Non-text
    emojis = ''.join(char for char in text if emoji.is_emoji(char))
    text = re.sub(r"[^a-zA-Z\s]", '', text)

    # Stop words
    tokens = word_tokenize(text)
    filtered = [word for word in tokens if word.lower() not in stop_words]

    filtered = ' '.join(filtered) + ' ' + emojis
    
    return filtered.strip()

def clean_comments(comments_raw):
    try:
        comments_list = ast.literal_eval(comments_raw)
        if isinstance(comments_list, list):
            cleaned = [(clean_text(comment), score) for comment, score in comments_list if isinstance(comment, str)]
            return cleaned
        else:
            return []
    except (ValueError, SyntaxError):
        return []

def main():
    input_file = 'data/reddit_posts/raw_post/shib/shiba_full_cleaned_final.csv'
    output_file = 'shiba.csv'

    df = pd.read_csv(input_file)

    # Clean full_text
    df['full_text'] = df['full_text'].apply(clean_text)

    # Clean comments
    df['comments'] = df['comments'].astype(str).apply(clean_comments)

    # Remove duplicates
    df = df.drop_duplicates(subset=['full_text'])

    df.to_csv(output_file, index=False)
    print('Done')

if __name__ == '__main__':
    main()
