import logging
import json

from app.models.article_element import ArticleElement
from app.utils.openai_client import translate_text
from app.utils.db import get_simplified_article_by_id, store_article
from app.utils.text_chuncking import logger

def translate_and_save_articles(simplified_article_ids, target_language, target_level):
    logging.info("Starting article translation and saving process.")

    for article_id in simplified_article_ids:
        try:
            simplified_article = get_simplified_article_by_id(article_id)
            if simplified_article is None:
                logging.error("Simplified article not found for ID %s", article_id)
                continue

            simplified_text_array = json.loads(simplified_article['simplified_text'])
            translated_text_array = []
            total_input_tokens = 0
            total_output_tokens = 0
            for chunk in simplified_text_array:
                if chunk['type'] == 'image':
                    translated_text_array.append(chunk)
                    continue
                translated_text, num_input_tokens, num_output_tokens = translate_text(chunk['content'], target_language, target_level)
                total_input_tokens += num_input_tokens
                total_output_tokens += num_output_tokens
                if translated_text is None:
                    logging.error("Text translation failed for chunk in %s", article_id)
                    continue
                translated_text_array.append(ArticleElement('paragraph', translated_text))

            logger.info(f"Text translation process completed successfully for {article_id}")

            translated_text_json = json.dumps([element.to_dict() for element in translated_text_array])
            if not store_article(article_id, simplified_article['original_url'], simplified_article['title'], translated_text_json, target_language, target_level, main_image_url):
                logging.error("Failed to store translated article for %s", article_id)
                continue

            logging.info("Translated article processed and stored successfully for %s", article_id)

        except Exception as e:
            logging.exception("An error occurred while processing the article %s: %s", article_id, str(e))

    logging.info("Article translation and saving process completed.")