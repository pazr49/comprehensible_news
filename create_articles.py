from app.routes.batch_generate_articles import batch_generate_articles
from app.routes.simplify_articles import scrape_chunk_simplify_articles
from app.utils.db import init_db
from app.utils.db import init_db

article_links = [
    "https://www.bbc.com/travel/article/20241008-chefs-guide-to-eating-in-bogota-colombia",
    "https://www.bbc.com/news/articles/c98zzderyr2o",
    "https://www.bbc.com/news/world-europe-65871238",
    "https://www.bbc.com/news/articles/cz5d5jz30v4o",
    "https://www.bbc.com/news/articles/c206l3qgnx2o",
    "https://www.bbc.com/news/articles/cz9x41gnkgqo",
    "https://www.bbc.com/news/entertainment-arts-64267366",
    "https://www.bbc.com/news/newsbeat-67449243",
    "https://www.bbc.com/news/newsbeat-64305760",
    "https://www.bbc.com/future/article/20241101-how-online-photos-and-videos-alter-the-way-you-think",
    "https://www.bbc.com/news/articles/c30p16gn3pvo",
    "https://www.bbc.com/news/articles/c86qy500545o",
    "https://www.bbc.com/news/world-latin-america-67826941",
    "https://www.bbc.com/future/article/20241111-stressed-writing-down-a-to-do-list-might-help",
    "https://www.bbc.com/future/article/20201028-the-benefits-of-coffee-is-coffee-good-for-health",
    "https://www.bbc.com/news/articles/ckgn18xl3j7o",
    "https://www.bbc.com/news/articles/ckg79y3rz1eo",
    "https://www.bbc.com/sport/boxing/articles/ceqxvxnyq7lo",
    "https://www.bbc.com/news/world-latin-america-66819339",
    "https://www.bbc.com/news/articles/c4gdkljn78ko"
]


init_db()

target_level = 'A2'

scrape_chunk_simplify_articles(article_links, "A1")
scrape_chunk_simplify_articles(article_links, "A2")
scrape_chunk_simplify_articles(article_links, "B1")

