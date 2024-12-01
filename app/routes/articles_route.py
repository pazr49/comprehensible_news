import logging
from flask import Blueprint, jsonify, request
from app.db.article_db import get_articles, get_article_by_id, get_articles_by_group_id, get_todays_articles, get_articles_by_tag
from app.utils.bbc_rss_reader import bbc_rss_reader

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a Blueprint for articles
articles_bp = Blueprint('articles', __name__)

# Route to get all articles
@articles_bp.route('/articles/', defaults={'language': 'en', 'level': "A1"}, methods=['GET'])
@articles_bp.route('/articles/<language>/', defaults={'level': 'A1'}, methods=['GET'])
@articles_bp.route('/articles/<language>/<level>', methods=['GET'])
def get_articles_route(language, level):
    try:
        logger.info(f"Fetching articles with language: {language} and level: {level}")
        articles = get_articles(language, level)
        if articles:
            logger.debug(f"Found {len(articles)} articles")
            return jsonify(articles)
        else:
            logger.warning("No articles found")
            return jsonify({'message': 'No articles found'}), 404
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return jsonify({'error': 'An error occurred while fetching articles'}), 500

# Route to get an article by ID
@articles_bp.route('/article_by_id', methods=['GET'])
def get_article():
    article_id = request.args.get('id')
    if not article_id:
        logger.error("Article ID is required")
        return jsonify({'error': 'Article ID is required'}), 400

    try:
        logger.debug(f"Fetching article with ID: {article_id}")
        article = get_article_by_id(article_id)
        if article:
            logger.debug(f"Found article: {article.title}")
            return jsonify(article.to_dict())
        else:
            logger.warning(f"Article with ID {article_id} not found")
            return jsonify({'error': 'Article not found'}), 404
    except Exception as e:
        logger.error(f"Error fetching article: {e}")
        return jsonify({'error': 'An error occurred while fetching the article'}), 500

# Route to get articles by group ID
@articles_bp.route('/article_group', defaults={'language': None}, methods=['GET'])
@articles_bp.route('/article_group/<language>', methods=['GET'])
def fetch_articles_by_group_id(language):
    article_group_id = request.args.get('id')
    if not article_group_id:
        logger.error("Article Group ID is required")
        return jsonify({'error': 'Article Group ID is required'}), 400

    try:
        logger.debug(f"Fetching articles with Group ID: {article_group_id} and language: {language}")
        articles = get_articles_by_group_id(article_group_id, language)
        if articles:
            logger.debug(f"Found {len(articles)} articles")
            return jsonify([article.to_dict() for article in articles])
        else:
            logger.warning(f"Articles with Group ID {article_group_id} not found")
            return jsonify({'error': 'Articles not found'}), 404
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return jsonify({'error': 'An error occurred while fetching the articles'}), 500

# Route to simplify and store articles
@articles_bp.route('/simplify_and_store_articles', methods=['POST'])
def simplify_and_store_articles_route():
    data = request.get_json()
    urls = data.get('urls')
    if not urls:
        logger.error("URLs are required")
        return jsonify({'error': 'URLs are required'}), 400

    try:
        from app.tasks.simplify_and_store_articles_task import simplify_and_store_articles_task
        simplify_and_store_articles_task.delay(urls)
        logger.info("Simplify and store articles task started")
        return jsonify({'message': 'Task started'}), 202
    except Exception as e:
        logger.error(f"Error starting simplify and store articles task: {e}")
        return jsonify({'error': 'An error occurred while starting the task'}), 500

# Route to translate and store articles
@articles_bp.route('/translate_and_store_articles', methods=['POST'])
def translate_and_store_articles_route():
    data = request.get_json()
    article_group_id = data.get('article_group_id')
    target_languages = data.get('target_languages')
    if not article_group_id:
        logger.error("Article Group ID is required")
        return jsonify({'error': 'Article Group ID is required'}), 400
    if not target_languages:
        logger.error("Target languages are required")
        return jsonify({'error': 'Target languages are required'}), 400

    try:
        from app.tasks.translate_and_store_articles_task import translate_and_store_articles_task
        translate_and_store_articles_task.delay(article_group_id, target_languages)
        logger.info("Translate and store articles task started")
        return jsonify({'message': 'Task started'}), 202
    except Exception as e:
        logger.error(f"Error starting translate and store articles task: {e}")
        return jsonify({'error': 'An error occurred while starting the task'}), 500

# Route to add articles from RSS feed
@articles_bp.route('/add_articles_from_rss_feed', methods=['POST'])
def add_articles_from_rss_feed():
    data = request.get_json()
    feed = data.get('feed')
    num_articles = data.get('num_articles')
    if not feed:
        logger.error("RSS feed URL is required")
        return jsonify({'error': 'RSS feed URL is required'}), 400
    if not num_articles:
        logger.error("Number of articles is required")
        return jsonify({'error': 'Number of articles is required'}), 400

    try:
        rss_articles = bbc_rss_reader(feed, num_articles)
        if not rss_articles:
            logger.error("Failed to read RSS feed")
            return jsonify({'error': 'Failed to read RSS feed'}), 500

        from app.tasks.simplify_and_store_articles_task import simplify_and_store_articles_task
        urls = [article.link for article in rss_articles]
        simplify_and_store_articles_task.delay(urls)
        logger.info("Add articles from RSS feed task started")
        return jsonify({'message': 'Task started'}), 202
    except Exception as e:
        logger.error(f"Error adding articles from RSS feed: {e}")
        return jsonify({'error': 'An error occurred while adding articles from RSS feed'}), 500


# Route to get today's articles
@articles_bp.route('/todays_articles', methods=['GET'])
def todays_articles():
    try:
        logger.info("Fetching today's articles")
        articles = get_todays_articles()
        if articles:
            logger.debug(f"Found {len(articles)} articles")
            return jsonify([article.to_dict() for article in articles])
        else:
            logger.warning("No articles found")
            return jsonify({'message': 'No articles found'}), 404
    except Exception as e:
        logger.error(f"Error fetching today's articles: {e}")
        return jsonify({'error': 'An error occurred while fetching today\'s articles'}), 500

# Route get articles by tag
@articles_bp.route('/articles_by_tag', methods=['GET'])
def articles_by_tag():
    tag = request.args.get('tag')
    language = request.args.get('language')
    if not tag:
        logger.error("Tag is required")
        return jsonify({'error': 'Tag is required'}), 400

    if not language:
        logger.error("Language is required")
        return jsonify({'error': 'Language is required'}), 400

    try:
        logger.info(f"Fetching articles with tag: {tag}")
        articles = get_articles_by_tag(tag=tag, language=language)
        if articles:
            logger.debug(f"Found {len(articles)} articles")
            return jsonify([article.to_dict() for article in articles])
        else:
            logger.warning(f"No articles found with tag: {tag}")
            return jsonify({'message': 'No articles found'}), 404
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return jsonify({'error': 'An error occurred while fetching articles'}), 500