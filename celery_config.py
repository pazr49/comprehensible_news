import os
from celery import Celery

# Check for Redis Cloud URL first, fallback to local Redis URL
redis_url = os.getenv('REDISCLOUD_URL', os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

# Create Celery app
celery_app = Celery('tasks',
                    broker=redis_url,
                    include=[
                        'app.tasks.simplify_and_store_articles_task',
                        'app.tasks.translate_and_store_articles_task'
                    ])

# Update Celery configuration
celery_app.conf.update(
    result_backend=redis_url,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
