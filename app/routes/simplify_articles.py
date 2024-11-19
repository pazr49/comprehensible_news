import logging
import uuid
import json

from app.models.article_element import ArticleElement
from app.utils.scraping import scrape_bbc
from app.utils.text_chuncking import split_text_into_chunks, logger
from app.utils.openai_client import simplify_text
from app.utils.db import store_simplified_article

def scrape_chunk_simplify_articles(article_links, target_level):
    logging.info("Starting article scraping, chunking, and simplification process.")

    for link in article_links:
        try:
            article_content, title = scrape_bbc(link)
            if article_content is None:
                logging.error("Article content extraction failed for %s", link)
                continue

            chunks = split_text_into_chunks(article_content, 300)
            logging.info(f"Text chunking process completed successfully for {link}")

            article_image_url = ''
            simplified_text_array = []
            total_input_tokens = 0
            total_output_tokens = 0
            for chunk in chunks:
                if chunk.type == 'image':
                    if article_image_url == '':
                        article_image_url = chunk.content
                        continue
                    simplified_text_array.append(chunk)
                    continue
                simplified_text, num_input_tokens, num_output_tokens = simplify_text(chunk.content, target_level)
                total_input_tokens += num_input_tokens
                total_output_tokens += num_output_tokens
                if simplified_text is None:
                    logging.error("Text simplification failed for chunk in %s", link)
                    continue
                simplified_text_array.append(ArticleElement('paragraph', simplified_text))

            logger.info(f"Text simplification process completed successfully for {link}")

            simplified_text_json = json.dumps([element.to_dict() for element in simplified_text_array])
            simplified_id = f'simplified_{uuid.uuid4().hex[:8]}'
            if not store_simplified_article(simplified_id, link, title, simplified_text_json, target_level, article_image_url, 'en'):
                logging.error("Failed to store simplified article for %s", link)
                continue

            logging.info("Simplified article processed and stored successfully for %s", link)

        except Exception as e:
            logging.exception("An error occurred while processing the article %s: %s", link, str(e))

    logging.info("Article scraping, chunking, and simplification process completed.")