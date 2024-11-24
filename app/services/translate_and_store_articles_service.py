import logging
import json
from app.models.article import Article
from app.db.article_db import store_article, get_articles_by_group_id
from app.utils.translator import translate_article
import random
import string



def translate_and_store_articles(article_group_id, target_languages):
    try:
        articles = get_articles_by_group_id(article_group_id)
    except Exception as e:
        logging.error(f"Failed to get article group '{article_group_id}': {e}")
        return

    if not articles:
        logging.error(f"Article group '{article_group_id}' not found")
        return

    for target_language in target_languages:
        for article in articles:
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
