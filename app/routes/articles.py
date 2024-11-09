from flask import Blueprint, current_app, jsonify
import requests

articles_bp = Blueprint('articles', __name__)

@articles_bp.route('/articles', methods=['GET'])
def get_articles():
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
