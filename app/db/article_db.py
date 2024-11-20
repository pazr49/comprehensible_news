import logging
import psycopg2
from app.db.db_connection import get_db_connection


def store_article(article):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if an article with the same URL, language, and level already exists
        cursor.execute('''
            SELECT id FROM articles WHERE original_url = %s AND language = %s AND level = %s
        ''', (article.original_url, article.language, article.level))
        existing_article = cursor.fetchone()

        if existing_article:
            # Update the existing article
            cursor.execute('''
                UPDATE articles
                SET article_id = %s, title = %s, translated_text = %s, image_url = %s, simplified_id = %s
                WHERE id = %s
            ''', (article.article_id, article.title, article.translated_text, article.image_url, existing_article[0], article.simplified_id))
        else:
            # Insert a new article
            cursor.execute('''
                INSERT INTO articles (article_id, original_url, title, translated_text, language, level, image_url, simplified_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (article.article_id, article.original_url, article.title, article.translated_text, article.language, article.level, article.image_url, article.simplified_id))

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
    cursor.execute('SELECT article_id, original_url, title, language, level, image_url, simplified_id FROM articles')
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
