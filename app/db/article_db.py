import logging
import psycopg2
from app.db.db import get_db_connection
from app.models.article import Article
from app.models.article_element import ArticleElement
import json

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

        if existing_article is not None:
            # Update the existing article
            cursor.execute('''
                UPDATE articles
                SET article_id = %s, title = %s, translated_text = %s, image_url = %s
                WHERE id = %s
            ''', (article.article_id, article.title, article.content, article.image_url, existing_article[0]))
        else:
            # Insert a new article
            cursor.execute('''
                INSERT INTO articles (article_id, original_url, title, content, language, level, image_url, article_group_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (article.article_id, article.original_url, article.title, article.content, article.language, article.level, article.image_url, article.article_group_id))

        conn.commit()
    except psycopg2.Error as e:
        logging.error(f"Error storing article in the database: {e}")
        return False
    finally:
        if conn:
            conn.close()
    return True

def get_articles(language='en', level='A1'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT article_id, original_url, title, language, level, image_url, article_group_id FROM articles WHERE language = %s AND level = %s', (language, level))
    articles = cursor.fetchall()
    conn.close()

    if articles:
        articles_list = [
            {
                'article_id': article[0],
                'original_url': article[1],
                'title': article[2],
                'language': article[3],
                'level': article[4],
                'image_url': article[5],
                'article_group_id': article[6]
            }
            for article in articles
        ]
        return articles_list
    return None

def get_article_by_id(article_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM articles WHERE article_id = %s', (article_id,))
    article = cursor.fetchone()
    conn.close()

    if article:
        content = json.loads(article[4])
        article_elements = [element.to_dict() for element in (ArticleElement.from_dict(e) for e in content)]

        article_dict = {
            'article_id': article[1],
            'original_url': article[2],
            'title': article[3],
            'content': article_elements,
            'language': article[5],
            'level': article[6],
            'image_url': article[7],
            'article_group_id': article[8]
        }
        return Article.from_dict(article_dict)
    return None

def get_article_by_url(original_url):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM articles WHERE original_url = %s', (original_url,))
    article = cursor.fetchone()
    conn.close()

    if article:
        content = json.loads(article[4])
        article_elements = [element.to_dict() for element in (ArticleElement.from_dict(e) for e in content)]

        article_dict = {
            'article_id': article[1],
            'original_url': article[2],
            'title': article[3],
            'content': article_elements,
            'language': article[5],
            'level': article[6],
            'image_url': article[7],
            'article_group_id': article[8]
        }
        return Article.from_dict(article_dict)
    return None


def get_articles_by_group_id(article_group_id, language=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if language:
        cursor.execute('SELECT * FROM articles WHERE article_group_id = %s AND language = %s',
                       (article_group_id, language))
    else:
        cursor.execute('SELECT * FROM articles WHERE article_group_id = %s', (article_group_id,))

    articles = cursor.fetchall()
    conn.close()

    if articles:
        articles_list = []
        for article in articles:
            content = json.loads(article[4])
            article_elements = [ArticleElement.from_dict(e) for e in content]
            article_obj = Article(
                article_id=article[1],
                original_url=article[2],
                title=article[3],
                content=article_elements,
                language=article[5],
                level=article[6],
                image_url=article[7],
                article_group_id=article[8]
            )
            articles_list.append(article_obj)
        return articles_list

    return None