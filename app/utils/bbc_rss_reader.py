# Description: This file contains the function to read the BBC RSS feed and return the top 5 articles from the feed.

import logging
import feedparser
from app.models.rss_article import RssArticle

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

bbc_rss_feeds = {
    "news": "https://feeds.bbci.co.uk/news/rss.xml",
    "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "uk": "https://feeds.bbci.co.uk/news/uk/rss.xml",
    "business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "politics": "https://feeds.bbci.co.uk/news/politics/rss.xml",
    "health": "https://feeds.bbci.co.uk/news/health/rss.xml",
    "education": "https://feeds.bbci.co.uk/news/education/rss.xml",
    "science": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "entertainment": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
}

def bbc_rss_reader(feed_name="news", num_articles=5):
    """
    Reads the BBC RSS feed and returns the top articles from the feed.

    :param feed_name: The name of the feed to read.
    :param num_articles: The number of articles to return.
    :return: A list of RssArticle objects.
    """
    feed_url = bbc_rss_feeds.get(feed_name)
    if not feed_url:
        logger.error(f"Feed name '{feed_name}' is not valid.")
        return []

    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo:
            logger.error(f"Failed to parse feed: {feed.bozo_exception}")
            return []

        articles = []
        for entry in feed.entries[:num_articles]:
            article = RssArticle(
                feed_name=feed_name,
                title=entry.get("title"),
                link=entry.get("link"),
                summary=entry.get("summary"),
                published=entry.get("published"),
                thumbnail=entry.get("media_thumbnail")
            )
            articles.append(article)
            logger.info(f"Article '{article.title}' added to the list.")

        logger.info(f"Successfully retrieved {len(articles)} articles from the '{feed_name}' feed.")
        return articles

    except Exception as e:
        logger.exception(f"An error occurred while reading the RSS feed: {e}")
        return []