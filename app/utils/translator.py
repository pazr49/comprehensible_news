import logging
from app.models.article_element import ArticleElement
from app.utils.openai_client import translate_text
from app.utils import logger

def translate_article(simplified_article, target_language, target_level):
    logging.info("Starting article translation process.")

    translated_text_array = []
    total_input_tokens = 0
    total_output_tokens = 0

    for chunk in simplified_article:
        if chunk.type == 'image':
            translated_text_array.append(chunk)
            continue

        try:
            translated_text, num_input_tokens, num_output_tokens = translate_text(chunk.content, target_language, target_level)
            if translated_text is None:
                raise ValueError("Translated text is None")
        except Exception as e:
            logging.error("Text translation failed for chunk: %s", str(e))
            continue

        total_input_tokens += num_input_tokens
        total_output_tokens += num_output_tokens
        translated_text_array.append(ArticleElement('paragraph', translated_text))

    logger.info("Text translation process completed successfully.")

    return translated_text_array, total_input_tokens, total_output_tokens