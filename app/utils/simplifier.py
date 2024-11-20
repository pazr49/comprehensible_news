import logging
from app.models.article_element import ArticleElement
from app.utils.openai_client import simplify_text
from app.utils import logger

def simplify_article(rss_article, article_chunks, target_level):
    simplified_text_array = []
    total_input_tokens = 0
    total_output_tokens = 0

    for chunk in article_chunks:
        if chunk.type == 'image':
            simplified_text_array.append(chunk)
            continue

        try:
            simplified_text, num_input_tokens, num_output_tokens = simplify_text(chunk.content, target_level)
            if simplified_text is None:
                raise ValueError("Simplified text is None")
        except Exception as e:
            logging.error("Text simplification failed for chunk in %s: %s", rss_article.link, str(e))
            continue

        total_input_tokens += num_input_tokens
        total_output_tokens += num_output_tokens
        simplified_text_array.append(ArticleElement('paragraph', simplified_text))

    logger.info("Text simplification process completed successfully for %s", rss_article.link)

    return simplified_text_array, total_input_tokens, total_output_tokens