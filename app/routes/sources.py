from flask import Blueprint, current_app, jsonify
import requests

sources_bp = Blueprint('sources', __name__)

@sources_bp.route('/sources', methods=['GET'])
def get_sources():
    api_url = 'https://api.thenewsapi.com/v1/news/sources'

    params = {
        'api_token': current_app.config['API_KEY'],
        'language': 'en',
    }

    response = requests.get(api_url, params=params)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to retrieve sources'}), response.status_code

    data = response.json()
    sources = data.get('data', [])

    return jsonify(sources)
