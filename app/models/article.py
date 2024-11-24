
class Article:
    def __init__(self, title, content, language, level, image_url, original_url, article_id, article_group_id):
        self.title = title
        self.content = content
        self.language = language
        self.level = level
        self.image_url = image_url
        self.original_url = original_url
        self.article_id = article_id
        self.article_group_id = article_group_id


    def __str__(self):
        return f"{self.title} - {self.language} - {self.level}"

    def to_dict(self):
        return {
            'title': self.title,
            'content': [element.to_dict() for element in self.content],
            'language': self.language,
            'level': self.level,
            'image_url': self.image_url,
            'original_url': self.original_url,
            'article_id': self.article_id,
            'article_group_id': self.article_group_id
        }

    @staticmethod
    def from_dict(article_dict):
        return Article(
            article_dict['title'],
            article_dict['content'],
            article_dict['language'],
            article_dict['level'],
            article_dict['image_url'],
            article_dict['original_url'],
            article_dict['article_id'],
            article_dict['article_group_id']
        )