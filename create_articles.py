from app.routes.batch_generate_articles import batch_generate_articles

article_links = [
    "https://www.bbc.com/news/articles/c8dm0ljg4y6o",
    "https://www.bbc.com/news/articles/c93716xdgzqo",
    "https://www.bbc.com/news/articles/c33em6jrx1go",
    "https://www.bbc.com/news/articles/c0mzgv4x901o",
    "https://www.bbc.com/sport/boxing/articles/ceqxvxnyq7lo",
    "https://www.bbc.com/news/articles/ckg79y3rz1eo",
    "https://www.bbc.com/news/articles/c206l3qgnx2o",
    "https://www.bbc.com/travel/article/20241008-chefs-guide-to-eating-in-bogota-colombia",
    "https://www.bbc.com/news/articles/ckgn18xl3j7o",
    "https://www.bbc.com/news/articles/c4gdkljn78ko",
    "https://www.bbc.com/news/articles/c98zzderyr2o",
    "https://www.bbc.com/news/articles/c86qy500545o",
    "https://www.bbc.com/news/newsbeat-67449243",
    "https://www.bbc.com/news/newsbeat-64305760",
    "https://www.bbc.com/news/entertainment-arts-64267366",
    "https://www.bbc.com/news/articles/c30p16gn3pvo",
    "https://www.bbc.com/future/article/20241111-stressed-writing-down-a-to-do-list-might-help",
    "https://www.bbc.com/future/article/20241101-how-online-photos-and-videos-alter-the-way-you-think",
    "https://www.bbc.com/future/article/20201028-the-benefits-of-coffee-is-coffee-good-for-health",
    "https://www.bbc.com/news/articles/cz9x41gnkgqo",
    "https://www.bbc.com/news/articles/cz5d5jz30v4o",
    "https://www.bbc.com/news/world-latin-america-67826941",
    "https://www.bbc.com/news/world-latin-america-66819339",
    "https://www.bbc.com/news/world-europe-65871238"
]


target_language = 'Spanish'
target_level = 'A2'

batch_generate_articles("Spanish", "A2", article_links)
batch_generate_articles("Spanish", "B1", article_links)
batch_generate_articles("French", "A1", article_links)
batch_generate_articles("French", "A2", article_links)

#heroku pg:push comprehensible_news DATABASE_URL --app comprehensiblenews
