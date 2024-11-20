from flask import Flask
from dotenv import load_dotenv
import os
from app.db.db import init_db
from flask_cors import CORS



def create_app():
    app = Flask(__name__)
    CORS(app)

    # Load environment variables
    load_dotenv()
    app.config['API_KEY'] = os.getenv('API_KEY')
    if not app.config['API_KEY']:
        raise ValueError("No API_KEY found in environment variables")

    # Initialize the database
    init_db()

    # Register Blueprints
    from app.routes.articles import articles_bp
    from app.routes.sources import sources_bp
    from app.routes.article_content import article_content_bp

    app.register_blueprint(articles_bp)
    app.register_blueprint(sources_bp)
    app.register_blueprint(article_content_bp)

    return app