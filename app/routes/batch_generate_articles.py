import logging
import uuid
import json

from flask import Blueprint, request, jsonify
from app.models.article_element import ArticleElement

from app.utils.scraping import scrape_bbc
from app.utils.text_chuncking import split_text_into_chunks, logger
from app.utils.openai_client import simplify_text, translate_text
from app.utils.db import store_article
batch_generate_articles_bp = Blueprint('batch_generate_articles', __name__)

article_links = [
    'https://www.bbc.com/news/articles/c8dm0ljg4y6o',
    'https://www.bbc.com/news/articles/c93716xdgzqo',
    'https://www.bbc.com/news/articles/c33em6jrx1go',
    'https://www.bbc.com/news/articles/c0mzgv4x901o',
    'https://www.bbc.com/sport/boxing/articles/ceqxvxnyq7lo',
    'https://www.bbc.com/news/articles/ckg79y3rz1eo',

]


@batch_generate_articles_bp.route('/batch_generate_articles', methods=['POST'])
def batch_generate_articles():
    # Log the start of the batch generation process
    logging.info("Starting batch article generation process.")

    target_language = request.args.get('target_language', 'fr')
    target_level = request.args.get('target_level', 'A1')

    data = request.get_json()
    if not data:
        logging.error("No data provided in the request.")
        return jsonify({'error': 'No data provided'}), 400

    translated_articles = []
    total_estimated_cost = 0
    for link in article_links:
        try:
            # Scrape the article content and title
            article_content, title = scrape_bbc(link)
            if article_content is None:
                logging.error("Article content extraction failed for %s", link)
                continue

            # Split the article content into chunks
            chunks = split_text_into_chunks(article_content, 300)
            assert isinstance(chunks, list) and all(
                isinstance(chunk, ArticleElement) for chunk in chunks), "chunks must be a list of ArticleElement"
            if chunks is None:
                logging.error("Text chunking failed for %s", link)
                continue

            simplified_text_array = []
            total_input_tokens = 0
            total_output_tokens = 0
            for chunk in chunks:
                if chunk.type == 'image':
                    simplified_text_array.append(chunk)
                    continue
                # Simplify each chunk of text
                simplified_text, num_input_tokens, num_output_tokens = simplify_text(chunk.content, target_level)
                total_input_tokens += num_input_tokens
                total_output_tokens += num_output_tokens
                if simplified_text is None:
                    logging.error("Text simplification failed for chunk in %s", link)
                    continue
                simplified_text_array.append(ArticleElement('paragraph', simplified_text))
            logger.info(f"Text simplification process completed successfully for {link}")

            #https://openai.com/api/pricing/
            estimated_cost_simplification = total_input_tokens * (0.15/1000000) + total_output_tokens * (0.6/1000000)
            logger.info(f"Estimated cost for simplification: ${estimated_cost_simplification}")

            # Translate the simplified text
            translated_text_array = []
            main_image_url = ''
            total_input_tokens = 0
            total_output_tokens = 0
            for chunk in simplified_text_array:
                if chunk.type == 'image':
                    if main_image_url == '':
                        main_image_url = chunk.content  # Assuming chunk.content contains the image URL
                        continue
                    else:
                        translated_text_array.append(chunk)
                    continue
                translated_text, num_input_tokens, num_output_tokens = translate_text(chunk.content, target_language,
                                                                                      target_level)
                total_input_tokens += num_input_tokens
                total_output_tokens += num_output_tokens
                if translated_text is None:
                    logging.error("Text translation failed for chunk in %s", link)
                    continue
                translated_text_array.append(ArticleElement('paragraph', translated_text))

            logger.info(f"Text translation process completed successfully for {link}")

            # Calculate the estimated cost for translation
            estimated_cost_of_translation = total_input_tokens * (0.15 / 1000000) + total_output_tokens * (0.6 / 1000000)
            logger.info(f"Estimated cost for translation: ${estimated_cost_of_translation}")

            # Store the translated article in the database
            translated_text_json = json.dumps([element.to_dict() for element in translated_text_array])
            article_id = f'article_{uuid.uuid4().hex[:8]}'
            if not store_article(article_id, link, title, translated_text_json, target_language, target_level, main_image_url):
                logging.error("Failed to store article for %s", link)
                continue

            logging.info("Article processed and stored successfully for %s", link)
            logging.info(f"Total estimated cost for article {article_id}: ${estimated_cost_simplification + estimated_cost_of_translation}")

            total_estimated_cost += estimated_cost_simplification + estimated_cost_of_translation

        except Exception as e:
            logging.exception("An error occurred while processing the article %s: %s", link, str(e))

    # Log the completion of the batch generation process
    logging.info("Batch article generation process completed.")
    logging.info(f"Total estimated cost: ${total_estimated_cost}")

    return jsonify(translated_articles)