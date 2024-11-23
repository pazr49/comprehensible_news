import logging
from flask import Blueprint, jsonify
from app.db.article_db import get_articles, get_article_by_id, get_articles_by_group_id
from flask import request

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

articles_bp = Blueprint('articles', __name__)

# Define the route to get all articles
@articles_bp.route('/articles/', defaults={'language': 'en', 'level': "A1"}, methods=['GET'])
@articles_bp.route('/articles/<language>/', defaults={'level': 'A1'}, methods=['GET'])
@articles_bp.route('/articles/<language>/<level>', methods=['GET'])
def get_articles_route(language, level):
    try:
        logger.info(f"Fetching articles with language: {language} and level: {level}")
        articles = get_articles(language, level)
        logger.debug(f"Found {len(articles)} articles")
        return jsonify(articles)
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return jsonify({'error': 'An error occurred while fetching articles'}), 500

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
            logger.error(f"Article with ID {article_id} not found")
            return jsonify({'error': 'Article not found'}), 404
    except Exception as e:
        logger.error(f"Error fetching article: {e}")
        return jsonify({'error': 'An error occurred while fetching the article'}), 500

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
            return jsonify([article for article in articles])
        else:
            logger.error(f"Articles with Group ID {article_group_id} not found")
            return jsonify({'error': 'Articles not found'}), 404
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return jsonify({'error': 'An error occurred while fetching the articles'}), 500