import logging
import uuid

from flask import Blueprint, request, jsonify

from app.utils.scraping import scrape_bbc
from app.utils.text_chuncking import split_text_into_chunks, logger
from app.utils.openai_client import simplify_text, translate_text
from app.utils.db import store_article
batch_generate_articles_bp = Blueprint('batch_generate_articles', __name__)

article_links = [
    'https://www.bbc.com/news/articles/c3vlndv0yxpo',
]


@batch_generate_articles_bp.route('/batch_generate_articles', methods=['POST'])
def batch_generate_articles():
    # Log the start of the batch generation process
    logging.info("Starting batch article generation process.")

    target_language = request.args.get('target_language', 'es')
    target_level = request.args.get('target_level', 'A2')

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
            if chunks is None:
                logging.error("Text chunking failed for %s", link)
                continue

            simplified_text_array = []
            total_input_tokens = 0
            total_output_tokens = 0
            for chunk in chunks:
                # Simplify each chunk of text
                simplified_text, num_input_tokens, num_output_tokens = simplify_text(chunk, target_level)
                total_input_tokens += num_input_tokens
                total_output_tokens += num_output_tokens
                if simplified_text is None:
                    logging.error("Text simplification failed for chunk in %s", link)
                    continue
                simplified_text_array.append(simplified_text)
            simplified_text = " ".join(simplified_text_array)
            logger.info(f"Text simplification process completed successfully for {link}")

            #https://openai.com/api/pricing/
            estimated_cost_simplification = total_input_tokens * (0.15/1000000) + total_output_tokens * (0.6/1000000)
            logger.info(f"Estimated cost for simplification: ${estimated_cost_simplification}")

            # Translate the simplified text
            translated_article, total_input_tokens, total_output_tokens = translate_text(simplified_text, target_language, target_level)
            if translated_article is None:
                logging.error("Text translation failed for %s", link)
                continue
            estimated_cost_of_translation = total_input_tokens * (0.15/1000000) + total_output_tokens * (0.6/1000000)
            logger.info(f"Estimated cost for translation: ${estimated_cost_of_translation}")

            article_id = f'article_{uuid.uuid4().hex[:8]}'
            # Store the translated article in the database
            if not store_article(article_id, link, title, translated_article, target_language, target_level):
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