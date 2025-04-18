from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from finvizfinance.quote import finvizfinance
from transformers import pipeline
from flask_cors import CORS
import pandas as pd

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load sentiment analysis model
sentiment_model = pipeline("sentiment-analysis")

# Analyze sentiment of a headline
def get_sentiment(text):
    result = sentiment_model(text)[0]
    return result['label'], result['score']

# Get headlines for a ticker within a time range
def get_headlines(ticker, time_range):
    stock = finvizfinance(ticker.upper())
    news_df = stock.ticker_news()

    current_time = datetime.now()
    time_offsets = {
        "1h": timedelta(hours=1),
        "6h": timedelta(hours=6),
        "1d": timedelta(days=1),
        "3d": timedelta(days=3)
    }
    start_time = current_time - time_offsets.get(time_range, timedelta(0))

    filtered = []
    for _, row in news_df.iterrows():
        try:
            headline_time = row['Date']
            if isinstance(headline_time, pd.Timestamp) and headline_time >= start_time:
                filtered.append(row)
        except Exception:
            continue

    return filtered

# API route: Sentiment analysis
@app.route('/get_sentiment', methods=['GET'])
def analyze_sentiment():
    ticker = request.args.get('ticker', '').upper()
    time_range = request.args.get('time_range', '1d')
    headlines = get_headlines(ticker, time_range)

    results = []
    total_score = 0
    positive_count = 0
    negative_count = 0

    for row in headlines:
        sentiment, score = get_sentiment(row['Title'])
        results.append({
            'headline': row['Title'],
            'sentiment': sentiment,
            'score': score
        })
        total_score += score
        if sentiment == 'POSITIVE':
            positive_count += 1
        elif sentiment == 'NEGATIVE':
            negative_count += 1

    overall_score = total_score / len(results) if results else 0

    return jsonify({
        'headlines': results,
        'overall_sentiment_score': overall_score,
        'positive_count': positive_count,
        'negative_count': negative_count
    })

# Root route
@app.route('/')
def home():
    return "✅ Flask backend is running."

# Run server
if __name__ == '__main__':
    app.run(debug=True)
