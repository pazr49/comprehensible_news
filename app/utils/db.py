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
            translated_text TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def store_article(article_id, original_url, title, translated_text):
    conn = None
    try:
        conn = sqlite3.connect('articles.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO articles (article_id, original_url, title, translated_text)
            VALUES (?, ?, ?, ?)
        ''', (article_id, original_url, title, translated_text))
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
    cursor.execute('SELECT * FROM articles')
    articles = cursor.fetchall()
    conn.close()
    return articles