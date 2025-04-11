import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt_tab')
nltk.download('stopwords')
import os

# Stop words
stop_words = set(stopwords.words('english'))

# Clean text
def clean_text(text):
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)

    # Remove mentions
    text = re.sub(r'@\w+', '', text)

    # Remove emojis and non-text
    text = text.encode('ascii', 'ignore').decode('ascii')

    # Remove punctuation and numbers
    text = re.sub(r'[^a-z\s]', '', text)

    # Tokenize and remove stop words
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]

    return ' '.join(tokens)

csv_files = ['pepe_posts.csv', 'shiba_posts.csv']

for input_file in csv_files:
    # Load csv file
    df = pd.read_csv(input_file)

    # Remove duplicates
    df.drop_duplicates(subset='title', inplace=True)

    # Clean titles
    df['title'] = df['title'].apply(clean_text)

    # Save data
    output_file = f"clean_{os.path.basename(input_file)}"
    df.to_csv(output_file, index=False)

print('Done')

