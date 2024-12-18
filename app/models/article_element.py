
class ArticleElement():
    def __init__(self, type, content):
        self.type = type
        self.content = content

    def to_dict(self):
        return {
            'type': self.type,
            'content': self.content
        }

    @staticmethod
    def from_dict(article_element_dict):
        return ArticleElement(
            article_element_dict['type'],
            article_element_dict['content']
        )

    def __str__(self):
        return f"ArticleElement({self.type}, {self.content})"

    def __repr__(self):
        return self.__str__()

