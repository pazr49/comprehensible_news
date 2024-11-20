import logging
import uuid
import json
from app.models.article import Article
from app.utils.bbc_rss_reader import bbc_rss_reader
from app.utils.scraper import scrape_and_chunk_article
from app.utils.simplifier import simplify_article
from app.db.rss_article_db import store_rss_article
from app.db.article_db import store_article
from app.db.db import init_db


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def add_new_articles_from_rss(rss_feed, num_articles):
    '''
    This function reads the RSS feed and stores the articles in the database.
    It then simplifies the articles and stores the simplified articles in the database for each language level.
    :param rss_feed: URL of the RSS feed to read articles from
    :param num_articles: Number of articles to fetch from the RSS feed
    :return: None
    '''

    target_levels = ["A1", "A2", "B1", "B2"]

    try:
        rss_feed = bbc_rss_reader(rss_feed, num_articles)
        logging.info(f"Read {len(rss_feed)} articles from the RSS feed")
    except Exception as e:
        logging.critical(f"Failed to read RSS feed: {e}")
        return

    for target_level in target_levels:
        for rss_article in rss_feed:
            print("printing article",  json.dumps(rss_article.to_dict()))
            try:
                # Store the rss_article in the database
                store_rss_article(rss_article)
                logging.info(f"Stored RSS article '{rss_article.title}' in the database")
            except Exception as e:
                logging.error(f"Failed to store RSS article '{rss_article.title}': {e}")

            try:
                chunked_article = scrape_and_chunk_article(rss_article)
            except Exception as e:
                logging.error(f"Failed to scrape and chunk article '{rss_article.title}': {e}")
                continue

            try:
                simplified_chunks, total_input_tokens, total_output_tokens = simplify_article(rss_article, chunked_article, target_level)
                simplified_chunks_json = json.dumps([chunk.to_dict() for chunk in simplified_chunks])
            except Exception as e:
                logging.error(f"Failed to simplify article '{rss_article.title}' at level '{target_level}': {e}")
                continue

            article_id = uuid.uuid4().hex
            simplified_article = Article(
                article_id=article_id,
                original_url=rss_article.link,
                title=rss_article.title,
                content=simplified_chunks_json,
                language="en",
                level=target_level,
                image_url=rss_article.thumbnail
            )

            try:
                # Store the simplified article in the database
                store_article(simplified_article)
                logging.info(f"Stored simplified article '{simplified_article.article_id}' at level '{target_level}' in the database")
            except Exception as e:
                logging.error(f"Failed to store simplified article '{simplified_article.article_id}' at level '{target_level}': {e}")


if __name__ == '__main__':
    init_db()

    add_new_articles_from_rss("news", 5)