from celery_config import celery_app
from app.services.simplify_and_store_articles_service import simplify_and_store_articles
from app.tasks.translate_and_store_articles_task import translate_and_store_articles_task
import logging

@celery_app.task
def simplify_and_store_articles_task(urls):
    logging.info(f"Simplifying URLs: {urls}")
    article_ids, group_ids = simplify_and_store_articles(urls)
    logging.info(f"Article IDs: {article_ids}")
    for group_id in group_ids:
        translate_and_store_articles_task(group_id, ['es', 'fr'])


