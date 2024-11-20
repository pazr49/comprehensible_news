import psycopg2
import logging
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

import psycopg2
import logging
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file (useful for local development)
if os.getenv('ENV', 'development') == 'development':  # Default to 'development'
    load_dotenv()

def get_db_connection():
    try:
        # Use Heroku DATABASE_URL if available
        DATABASE_URL = os.getenv('DATABASE_URL')
        if DATABASE_URL:
            logging.info("Using Heroku DATABASE_URL.")
            return psycopg2.connect(DATABASE_URL)
        else:
            logging.warning("DATABASE_URL not found, falling back to local database configuration.")
            return psycopg2.connect(
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT')
            )
    except Exception as e:
        logging.error(f"Failed to connect to the database: {e}")
        raise


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            article_id TEXT NOT NULL,
            original_url TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            language TEXT NOT NULL,
            level TEXT NOT NULL,
            image_url TEXT, 
        )
    ''')

    cursor.execute('''
         CREATE TABLE IF NOT EXISTS rss_articles (
             id SERIAL PRIMARY KEY,
             title TEXT NOT NULL,
             url TEXT NOT NULL,
             thumbnail TEXT
             summary TEXT
             published_at TEXT
         )
         ''')

    conn.commit()
    conn.close()

