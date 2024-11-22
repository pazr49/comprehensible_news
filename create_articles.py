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
from app.db.article_db import get_article_by_id
from app.utils.translator import translate_article
import random
import string



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

    target_levels = ["A1", "A2", "B1"]
    chunk_size = 500

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
                chunked_article = scrape_and_chunk_article(rss_article, chunk_size)
            except Exception as e:
                logging.error(f"Failed to scrape and chunk article '{rss_article.title}': {e}")
                continue

            try:
                simplified_chunks, total_input_tokens, total_output_tokens = simplify_article(rss_article, chunked_article, target_level)
                simplified_chunks_json = json.dumps([chunk.to_dict() for chunk in simplified_chunks])
            except Exception as e:
                logging.error(f"Failed to simplify article '{rss_article.title}' at level '{target_level}': {e}")
                continue

            article_id = f"article_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
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


def translate_and_store_articles(article_ids, target_languages):

    for target_language in target_languages:
        for article_id in article_ids:
            # Get the article from the database
            article = get_article_by_id(article_id)
            if not article:
                logging.error(f"Article with ID '{article_id}' not found in the database")
                continue

            try:
                translated_chunks, total_input_tokens, total_output_tokens = translate_article(article, target_language)
            except Exception as e:
                logging.error(f"Failed to translate article '{article.article_id}': {e}")
                continue

            translated_chunks_json = json.dumps([chunk.to_dict() for chunk in translated_chunks])

            translated_article_id = f"article_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"

            translated_article = Article(
                article_id=translated_article_id,
                original_url=article.original_url,
                title=article.title,
                content=translated_chunks_json,
                language=target_language,
                level=article.level,
                image_url=article.image_url
            )

            try:
                # Store the translated article in the database
                store_article(translated_article)
                logging.info(f"Stored translated article '{translated_article.article_id}' in the database")
            except Exception as e:
                logging.error(f"Failed to store translated article '{translated_article.article_id}': {e}")



if __name__ == '__main__':
    init_db()

    target_languages = ["es", "fr"]

    article_ids = [
    "article_or4mwft5",
    "article_zzfiggbz",
    "article_nne6t3oh",
    "article_nt6o7cs4",
    "article_0z3v7eus",
    "article_yjwizf4w",
    "article_qj522bs4",
    "article_sw2wzppy",
    "article_2fdxit5u",
    "article_fh5jn0x5",
    "article_qsnc4lul",
    "article_guovcse7",
    "article_v5sfiyzj",
    "article_abjv6erj",
    "article_q2d0iw93"
    ]

    translate_and_store_articles(article_ids, target_languages)