from flask import Blueprint, current_app, jsonify
import requests
from app.db.db import get_articles, get_article_by_id, get_simplified_articles, get_article_by_simplified_id
from flask import request

articles_bp = Blueprint('articles', __name__)

@articles_bp.route('/articles_newsapi', methods=['GET'])
def get_articles_newsapi():
    api_url = 'https://api.thenewsapi.com/v1/news/all'

    params = {
        'api_token': current_app.config['API_KEY'],
        'language': 'en',
        'domains': 'bbc.com',
    }

    response = requests.get(api_url, params=params)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to retrieve articles'}), response.status_code

    data = response.json()
    articles = data.get('data', [])

    return jsonify(articles)

# Define the route to get all articles
@articles_bp.route('/articles', methods=['GET'])
def get_articles_route():
    articles = get_articles()
    articles_list = [
        {
            'article_id': article[0],
            'original_url': article[1],
            'title': article[2],
            'language': article[3],
            'level': article[4],
            'image_url': article[5]
        }
        for article in articles
    ]
    return jsonify(articles_list)

@articles_bp.route('/article_by_id', methods=['GET'])
def get_article():
    article_id = request.args.get('id')
    if not article_id:
        return jsonify({'error': 'Article ID is required'}), 400

    article = get_article_by_id(article_id)
    if article:
        article_dict = {
            'index': 1,
            'article_id': article[1],
            'original_url': article[2],
            'title': article[3],
            'simplified_text': article[4],
            'language': article[5],
            'level': article[6],
            'image_url': article[7]
        }
        return jsonify(article_dict)
    else:
        return jsonify({'error': 'Article not found'}), 404

# Get all the simplified articles
@articles_bp.route('/simplified_articles', methods=['GET'])
def fetch_simplified_articles():
    articles = get_simplified_articles()
    articles_list = [
        {
            'simplified_id': article[0],
            'original_url': article[1],
            'title': article[2],
            'simplified_text': article[3],
            'language': article[4],
            'level': article[5],
            'image_url': article[6]
        }
        for article in articles
    ]
    return jsonify(articles_list)

@articles_bp.route('/articles/<simplified_id>', methods=['GET'])
def fetch_article_by_simplified_id(simplified_id):
    language = request.args.get('language')
    level = request.args.get('level')

    article = get_article_by_simplified_id(simplified_id)

    if article:
        if (language and article[4] != language) or (level and article[5] != level):
            return jsonify({'error': 'Article not found with the specified filters'}), 404

        article_dict = {
            'article_id': article[0],
            'original_url': article[1],
            'title': article[2],
            'translated_text': article[3],
            'language': article[4],
            'level': article[5],
            'image_url': article[6]
        }
        return jsonify(article_dict)
    else:
        return jsonify({'error': 'Article not found'}), 404