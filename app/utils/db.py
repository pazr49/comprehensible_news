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
            translated_text TEXT NOT NULL,
            language TEXT NOT NULL,
            level TEXT NOT NULL,
            image_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

def store_article(article_id, original_url, title, translated_text, language, level, image_url=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if an article with the same URL, language, and level already exists
        cursor.execute('''
            SELECT id FROM articles WHERE original_url = %s AND language = %s AND level = %s
        ''', (original_url, language, level))
        existing_article = cursor.fetchone()

        if existing_article:
            # Update the existing article
            cursor.execute('''
                UPDATE articles
                SET article_id = %s, title = %s, translated_text = %s, image_url = %s
                WHERE id = %s
            ''', (article_id, title, translated_text, image_url, existing_article[0]))
        else:
            # Insert a new article
            cursor.execute('''
                INSERT INTO articles (article_id, original_url, title, translated_text, language, level, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (article_id, original_url, title, translated_text, language, level, image_url))

        conn.commit()
    except psycopg2.Error as e:
        logging.error(f"Error storing article in the database: {e}")
        return False
    finally:
        if conn:
            conn.close()
    return True

def get_articles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT article_id, original_url, title, language, level, image_url FROM articles')
    articles = cursor.fetchall()
    conn.close()
    return articles

def get_article_by_id(article_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM articles WHERE article_id = %s', (article_id,))
    article = cursor.fetchone()
    conn.close()
    return article