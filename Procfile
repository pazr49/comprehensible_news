web: gunicorn run:app
worker: celery -A celery_config.celery_app worker --loglevel=info