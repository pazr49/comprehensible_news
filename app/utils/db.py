import sqlite3
import logging
import logging

def init_db():
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id TEXT NOT NULL,
            original_url TEXT NOT NULL,
            title TEXT NOT NULL,
            translated_text TEXT NOT NULL, 
            language TEXT NOT NULL,
            level INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def store_article(article_id, original_url, title, translated_text, language, level):
    conn = None
    try:
        conn = sqlite3.connect('articles.db')
        cursor = conn.cursor()

        # Check if an article with the same URL, language, and level already exists
        cursor.execute('''
            SELECT id FROM articles WHERE original_url = ? AND language = ? AND level = ?
        ''', (original_url, language, level))
        existing_article = cursor.fetchone()

        if existing_article:
            # Update the existing article
            cursor.execute('''
                UPDATE articles
                SET article_id = ?, title = ?, translated_text = ?
                WHERE id = ?
            ''', (article_id, title, translated_text, existing_article[0]))
        else:
            # Insert a new article
            cursor.execute('''
                INSERT INTO articles (article_id, original_url, title, translated_text, language, level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (article_id, original_url, title, translated_text, language, level))

        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error storing article in the database: {e}")
        return False
    finally:
        if conn:
            conn.close()
    return True

def get_articles():
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    cursor.execute('SELECT article_id, original_url, title, language, level FROM articles')
    articles = cursor.fetchall()
    conn.close()
    return articles

def get_article_by_id(article_id):
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM articles WHERE article_id = ?', (article_id,))
    article = cursor.fetchone()
    conn.close()
    return article