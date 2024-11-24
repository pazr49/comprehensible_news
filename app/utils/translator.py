import logging
from app.models.article_element import ArticleElement
from app.utils.openai_client import open_ai_translate_text
from app.utils import logger
from translate import Translator

def translate_text(text, target_language):
    translator = Translator(to_lang=target_language)
    translation = translator.translate(text)
    return translation

def translate_article(article, target_language):
    logging.info("Starting article translation process.")

    translated_text_array = []
    total_input_tokens = 0
    total_output_tokens = 0

    for element in article.content:
        if element.type == 'image':
            translated_text_array.append(ArticleElement('image', element.content))
            continue
        if element.type == 'header':
            translated_header = translate_text(element.content, target_language)  # Translate to Spanish
            translated_text_array.append(ArticleElement('header', translated_header))
            continue
        try:
            translated_text, num_input_tokens, num_output_tokens = open_ai_translate_text(element.content, target_language, article.level)
            if translated_text is None:
                raise ValueError("Translated text is None")
        except Exception as e:
            logging.error("Text translation failed for element: %s", str(e))
            continue

        total_input_tokens += num_input_tokens
        total_output_tokens += num_output_tokens
        translated_text_array.append(ArticleElement('paragraph', translated_text))

    logger.info("Text translation process completed successfully.")

    return translated_text_array, total_input_tokens, total_output_tokens