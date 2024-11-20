
class RssArticle:
    def __init__(self, title, link, summary, published, thumbnail, feed_name):
        self.title = title
        self.link = link
        self.summary = summary
        self.published = published
        self.thumbnail = thumbnail
        self.feed_name = feed_name


    def to_dict(self):
        return {
            "title": self.title,
            "url": self.link,
            "summary": self.summary,
            "published": self.published,
            "thumbnail": self.thumbnail,
            "feed_name": self.feed_name
        }