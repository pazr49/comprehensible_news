
from app.db.db import get_db_connection
from app.models.rss_article import RssArticle

# takes a rss_article and stores it in the database
def store_rss_article(rss_article: RssArticle):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if an article with the same URL already exists
        cursor.execute('''
            SELECT id FROM rss_articles WHERE url = %s
        ''', (rss_article.link,))
        existing_article = cursor.fetchone()

        if existing_article:
            # Update the existing article
            cursor.execute('''
                UPDATE rss_articles
                SET title = %s, thumbnail = %s, summary = %s, published_at = %s
                WHERE id = %s
            ''', (rss_article.title, rss_article.thumbnail, rss_article.summary, rss_article.published, existing_article[0]))
        else:
            # Insert a new article
            cursor.execute('''
                INSERT INTO rss_articles (title, url, thumbnail, summary, published_at, feed_name)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (rss_article.title, rss_article.link, rss_article.thumbnail, rss_article.summary, rss_article.published, rss_article.feed_name))

        conn.commit()
    except Exception as e:
        print(f"Error storing RSS article in the database: {e}")
        return False
    finally:
        if conn:
            conn.close()
    return True


# returns all rss_articles from the database
def get_rss_articles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT title, url, thumbnail, summary, published_at, feed_name FROM rss_articles')
    rss_articles = cursor.fetchall()
    conn.close()
    return rss_articles


