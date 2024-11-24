import logging
import json
import gc
from app.models.article import Article
from app.utils.scraper import scrape_and_chunk_article
from app.utils.simplifier import simplify_article
from app.db.article_db import store_article, get_article_by_url
import random
import string

def simplify_and_store_articles(urls):
    target_levels = ["A1", "A2", "B1"]
    chunk_size = 500
    article_ids = []
    group_ids = []

    for url in urls:
        if get_article_by_url(url):
            logging.info(f"Article '{url}' already exists in the database")
            continue

        article_group_id = f"article_group_{''.join(random.choices(string.ascii_lowercase + string.digits, k=12))}"
        group_ids.append(article_group_id)
        for target_level in target_levels:
            try:
                chunked_article, title, thumbnail = scrape_and_chunk_article(url, chunk_size)
                logging.info(f"Scraped and chunked url '{url}'")
            except Exception as e:
                logging.error(f"Failed to scrape and chunk url '{url}': {e}")
                continue

            try:
                simplified_chunks, total_input_tokens, total_output_tokens = simplify_article(url, chunked_article, target_level)
                logging.info(f"Simplified url '{url}' at level '{target_level}'")
            except Exception as e:
                logging.error(f"Failed to simplify url '{url}' at level '{target_level}': {e}")
                continue

            article_id = f"article_{''.join(random.choices(string.ascii_lowercase + string.digits, k=12))}"
            simplified_article = Article(
                article_id=article_id,
                original_url=url,
                title=title,
                content=json.dumps([chunk.to_dict() for chunk in simplified_chunks]),
                language="en",
                level=target_level,
                image_url=thumbnail,
                article_group_id=article_group_id
            )

            article_ids.append(article_id)
            try:
                store_article(simplified_article)
                logging.info(f"Stored simplified url '{simplified_article.article_id}' at level '{target_level}' in the database")
            except Exception as e:
                logging.error("Failed to store simplified url '%s' at level '%s': %s", simplified_article.article_id, target_level, e)
                continue

            # Free memory
            del chunked_article, simplified_chunks, simplified_article
            gc.collect()

    return article_ids, group_ids