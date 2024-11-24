from celery_config import celery_app
from app.services.simplify_and_store_articles_service import simplify_and_store_articles

@celery_app.task
def simplify_and_store_articles_task(urls):
    print("Simplifying and storing articles")
    simplify_and_store_articles(urls)