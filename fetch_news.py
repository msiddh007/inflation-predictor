import os
import time
import pandas as pd
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

API_KEY = 'c8bf5aea000846b6b6c67d97c2872fc6'
newsapi = NewsApiClient(api_key=API_KEY)
analyzer = SentimentIntensityAnalyzer()

def fetch_econ_news_by_day(days_back=90):
    all_articles = []

    today = datetime.today()
    start_date = today - timedelta(days=days_back)

    print(f"📅 Fetching news from {start_date.date()} to {today.date()} by day...")

    for i in range(days_back):
        date = (start_date + timedelta(days=i)).date()
        from_param = to_param = date.strftime('%Y-%m-%d')

        try:
            response = newsapi.get_everything(
                q='inflation OR unemployment OR economy OR fed OR tariffs',
                language='en',
                sort_by='publishedAt',
                from_param=from_param,
                to=to_param,
                page_size=100,
            )

            articles = response.get('articles', [])
            for a in articles:
                text = f"{a.get('title', '')} {a.get('description', '')}".lower()
                sentiment = analyzer.polarity_scores(text)['compound']

                inflation_flag = any(word in text for word in ['inflation', 'cpi', 'pce', 'ppi', 'prices', 'cost of living'])
                unemployment_flag = any(word in text for word in ['unemployment', 'jobless', 'labor market', 'jobs', 'layoffs'])

                all_articles.append({
                    'title': a.get('title'),
                    'description': a.get('description'),
                    'publishedAt': a.get('publishedAt'),
                    'source': a['source']['name'],
                    'sentiment': sentiment,
                    'inflation_related': inflation_flag,
                    'unemployment_related': unemployment_flag
                })

            print(f"📆 {from_param}: {len(articles)} articles")
            time.sleep(1)

        except Exception as e:
            print(f"⚠️ Error fetching for {from_param}: {e}")
            time.sleep(1)

    df = pd.DataFrame(all_articles)

    if not df.empty:
        df['publishedAt'] = pd.to_datetime(df['publishedAt'])
        os.makedirs('data/raw', exist_ok=True)
        df.to_csv('data/raw/daily_news.csv', index=False)
        print(f"✅ Saved {len(df)} total articles to: data/raw/daily_news.csv")
    else:
        print("❌ No articles fetched.")
    return df


def create_sentiment_scores(df):
    df['date'] = df['publishedAt'].dt.date
    grouped = df.groupby('date')

    inflation_sentiment = (
        df[df['inflation_related']]
        .groupby('date')['sentiment']
        .mean()
        .rename('inflation_sentiment')
    )

    unemployment_sentiment = (
        df[df['unemployment_related']]
        .groupby('date')['sentiment']
        .mean()
        .rename('unemployment_sentiment')
    )

    combined = pd.concat([inflation_sentiment, unemployment_sentiment], axis=1).reset_index()
    combined['date'] = pd.to_datetime(combined['date'])

    os.makedirs('data/raw', exist_ok=True)
    combined.to_csv('data/raw/daily_news_sentiment.csv', index=False)
    print(f"✅ Saved daily sentiment scores to: data/raw/daily_news_sentiment.csv")

if __name__ == '__main__':
    news_df = fetch_econ_news_by_day(days_back=90)
    if not news_df.empty:
        create_sentiment_scores(news_df)
