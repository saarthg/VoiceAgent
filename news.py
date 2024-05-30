from newsapi import NewsApiClient
import os
from langchain_core.tools import tool

@tool
def get_latest_news(topic):
    """Fetches and prints the top headlines for a certain news topic. Takes in news topic.
    """
    newsapi = NewsApiClient(os.getenv("NEWS_API_KEY"))

    top_headlines = newsapi.get_top_headlines(q=topic,
                                          language='en',
                                          country='us')
    for article in top_headlines["articles"]:
        print(article["title"])

