# Forecasting Price Movements in Memecoin Markets through Social Media Sentiment

In this work, we investigate the predictive relationship between social media sentiment and short-term price volatility in memecoin markets. By employing sentiment analysis models and supervised machine learning techniques, we seek to determine whether sentiment indicators from Reddit can serve as reliable predictors for price movements in DOGE, SHIB, and PEPE coin. Created by Sarika Ahire, Marvin Chen, and Ethan Puckett.

## Get price data
Run `src/crypto_price/get_price_data.py` to get OHLCV (Open, High, Low, Close, Volume) price data for the memecoins. `symbols`, `currency`, `start_date`, and `end_date` can be modified. To get a CryptoCompare API key, sign up at https://www.cryptocompare.com, go to the API section in your dashboard, and generate a new API key.

Our price data can be found under `data/crypto_price`.

## Web scraping
Run `src/reddit_scrape/reddit_scrape.py` to scrape Reddit.

Our Reddit posts can be found under `data/reddit_posts/raw_post`.

## Preprocessing
Run `src/reddit_scrape/preprocess_wo_emoji.py` to perform preprocessing on the Reddit posts and remove emojis (Baseline). Run `src/reddit_scrape/preprocess.py` to perform preprocessing on the Reddit posts and keep emojis.

Our Reddit posts with preprocessing can be found under `data/reddit_posts/preprocessed_post`.

## Sentiment analysis
Run `src/ml_training/sentiment_analysis/reddit_sentiment.py` to perform sentiment analysis with VADER and FinBERt. Run `src/ml_training/sentiment_analysis/llama4_sentiment.py` to perform sentiment analysis with Llama-4.

Our Reddit posts with sentiment analysis can be found under `data/reddit_posts/post_sentiment`.

## Predict price movements
Run `src/ml_training/ml_models/logistic_regression.ipynb` to predict whether prices increase or decrease using our Logistic Regression classifier (Baseline). Run `src/ml_training/ml_models/random_forest.ipynb` for our Random Forest classifier.

Run `src/ml_training/ml_models/CatBoostClassifier.ipynb` to predict prices using our CatBoostRegressor.
