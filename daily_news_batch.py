import logging
from app.services.simplify_and_store_articles_service import simplify_and_store_articles
from app.services.translate_and_store_articles_service import translate_and_store_articles
from app.utils.bbc_rss_reader import bbc_rss_reader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def daily_news_batch():
    """
    Fetches articles from various BBC RSS feeds, simplifies them, and translates them into specified languages.
    """
    rss_feeds = ["world", "uk", "technology", "politics", "latin_america", "europe"]

    for feed in rss_feeds:
        try:
            # Fetch articles from the RSS feed
            articles = bbc_rss_reader(feed, 5)
            if not articles:
                logger.warning(f"No articles found for feed '{feed}'")
                continue

            urls = [article.link for article in articles]

            # Simplify and store articles
            article_ids, group_ids = simplify_and_store_articles(urls)
            if not article_ids:
                logger.warning(f"No articles were simplified for feed '{feed}'")
                continue

            # Translate and store articles
            for group_id in group_ids:
                translate_and_store_articles(group_id, ["es", "fr"])

        except Exception as e:
            logger.error(f"An error occurred while processing feed '{feed}': {e}")

if __name__ == "__main__":
    daily_news_batch()