from celery_config import celery_app
from app.services.translate_and_store_articles_service import translate_and_store_articles

@celery_app.task
def translate_and_store_articles_task(group_id, languages):
    print("Translating and storing articles")
    translate_and_store_articles(group_id, languages)