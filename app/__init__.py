from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)

    # Load environment variables
    load_dotenv()
    app.config['API_KEY'] = os.getenv('API_KEY')
    if not app.config['API_KEY']:
        raise ValueError("No API_KEY found in environment variables")

    # Register Blueprints
    from app.routes.articles import articles_bp
    from app.routes.sources import sources_bp
    from app.routes.article_content import article_content_bp

    app.register_blueprint(articles_bp)
    app.register_blueprint(sources_bp)
    app.register_blueprint(article_content_bp)

    return app
