import json
import logging
import random
import string

from app.services.simplify_and_store_articles_service import simplify_and_store_articles

simplify_and_store_articles(["https://www.bbc.com/news/world-europe-58486391"])