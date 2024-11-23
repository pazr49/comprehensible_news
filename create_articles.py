import logging
import uuid
import json
from app.models.article import Article
from app.models.rss_article import RssArticle
from app.utils.bbc_rss_reader import bbc_rss_reader
from app.utils.scraper import scrape_and_chunk_article
from app.utils.simplifier import simplify_article
from app.db.rss_article_db import store_rss_article
from app.db.article_db import store_article, get_article_by_url
from app.db.db import init_db
from app.db.article_db import get_article_by_id
from app.utils.translator import translate_article
import feedparser
import random
import string


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_article_info_from_link(feed_url, article_link):
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        if entry.link == article_link:
            thumbnail_url = entry.get("media_thumbnail")[0]['url'] if entry.get("media_thumbnail") else None
            if thumbnail_url:
                thumbnail_url = thumbnail_url.replace('/240/', '/1536/')
            return RssArticle(
                title=entry.get("title"),
                link=entry.get("link"),
                summary=entry.get("summary"),
                published=entry.get("published"),
                thumbnail=thumbnail_url,
                feed_name=feed_url
            )
    return None

def add_new_articles_from_rss(rss_feed, num_articles, article_list=None):
    '''
    This function reads the RSS feed and stores the articles in the database.
    It then simplifies the articles and stores the simplified articles in the database for each language level.
    :param article_list:
    :param rss_feed: URL of the RSS feed to read articles from
    :param num_articles: Number of articles to fetch from the RSS feed
    :return: None
    '''

    target_levels = ["A1", "A2", "B1"]
    chunk_size = 500
    article_ids = []

    if not article_list:
        logging.info("No article list provided. Reading articles from the RSS feed.")
        try:
            articles = bbc_rss_reader(rss_feed, num_articles)
            logging.info(f"Read {len(rss_feed)} articles from the RSS feed")
        except Exception as e:
            logging.critical(f"Failed to read RSS feed: {e}")
            return
    else:
        logging.info("Using provided article list instead of reading from the RSS feed")
        articles = article_list

    for rss_article in articles:

        # Check if the article already exists in the database
        if get_article_by_url(rss_article.link):
            logging.info(f"Article '{rss_article.title}' already exists in the database")
            continue

        article_group_id = f"article_group_{''.join(random.choices(string.ascii_lowercase + string.digits, k=12))}"
        try:
            # Store the rss_article in the database
            store_rss_article(rss_article)
            logging.info(f"Stored RSS article '{rss_article.title}' in the database")
        except Exception as e:
            logging.error(f"Failed to store RSS article '{rss_article.title}': {e}")
            return None

        for target_level in target_levels:
            try:
                chunked_article = scrape_and_chunk_article(rss_article, chunk_size)
                logging.info(f"Scraped and chunked article '{rss_article.title}'")
            except Exception as e:
                logging.error(f"Failed to scrape and chunk article '{rss_article.title}': {e}")
                continue

            try:
                simplified_chunks, total_input_tokens, total_output_tokens = simplify_article(rss_article, chunked_article, target_level)
                simplified_chunks_json = json.dumps([chunk.to_dict() for chunk in simplified_chunks])
                logging.info(f"Simplified article '{rss_article.link}' at level '{target_level}'")
            except Exception as e:
                logging.error(f"Failed to simplify article '{rss_article.link}' at level '{target_level}': {e}")
                return None

            article_id = f"article_{''.join(random.choices(string.ascii_lowercase + string.digits, k=12))}"
            simplified_article = Article(
                article_id=article_id,
                original_url=rss_article.link,
                title=rss_article.title,
                content=simplified_chunks_json,
                language="en",
                level=target_level,
                image_url=rss_article.thumbnail,
                article_group_id=article_group_id
            )

            article_ids.append(article_id)
            try:
                # Store the simplified article in the database
                store_article(simplified_article)
                logging.info(f"Stored simplified article '{simplified_article.article_id}' at level '{target_level}' in the database")

            except Exception as e:
                logging.error("Failed to store simplified article '%s' at level '%s': %s",simplified_article.article_id, target_level, e)
                return None

    return article_ids


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

            translated_article_id = f"article_{''.join(random.choices(string.ascii_lowercase + string.digits, k=12))}"

            translated_article = Article(
                article_id=translated_article_id,
                original_url=article.original_url,
                title=article.title,
                content=translated_chunks_json,
                language=target_language,
                level=article.level,
                image_url=article.image_url,
                article_group_id=article.article_group_id
            )

            try:
                # Store the translated article in the database
                store_article(translated_article)
                logging.info(f"Stored translated article '{translated_article.article_id}' in the database")
            except Exception as e:
                logging.error(f"Failed to store translated article '{translated_article.article_id}': {e}")



if __name__ == '__main__':
    init_db()

    rss_article = RssArticle(
        title="Author Gabriel Garcia Marquez dies",
        link="https://www.bbc.com/news/world-latin-america-27073911",
        thumbnail="https://ichef.bbci.co.uk/ace/standard/624/mcs/media/images/74045000/jpg/_74045377_74045376.jpg",
        published="14 Apr 2024",
        summary="Nobel prize-winning Colombian author Gabriel Garcia Marquez has died in Mexico aged 87, his family says.",
        feed_name="Colombia",
    )

    rss_article2 = RssArticle(
        title="Gabriel Garcia Marquez: Guide to surreal and real Latin America",
        link="https://www.bbc.com/news/world-latin-america-27100627",
        thumbnail="https://ichef.bbci.co.uk/ace/standard/624/mcs/media/images/74352000/jpg/_74352527_316e581f-3bd9-4116-800e-f7c6d8d4852c.jpg",
        published="21 Apr 2014",
        summary="In the mid-1980s as a young undergraduate student of Latin American politics, to me Gabriel Garcia Marquez was as much a political historian as he was a writer of fantastical novels.",
        feed_name="Colombia",
    )

    articles = [rss_article, rss_article2]

    article_ids = add_new_articles_from_rss("", 0, articles)

    translate_and_store_articles(article_ids, ["es", "fr"])
