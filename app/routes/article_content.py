import logging
from flask import Blueprint, request, jsonify
import requests
from bs4 import BeautifulSoup
from app.utils.openai_client import simplify_text

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

article_content_bp = Blueprint('article_content', __name__)

def scrape_bbc(url):
    logger.debug("Starting scrape_bbc function with URL: %s", url)

    # Send a GET request to the page
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the request returned an unsuccessful status code
    except requests.RequestException as e:
        logger.error("Error retrieving the page: %s", e)
        return None, None

    logger.debug("Page retrieved successfully. Status Code: %s", response.status_code)

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the title from the headline block
    title_tag = soup.find('div', {'data-component': 'headline-block'})
    title = title_tag.find('h1').get_text(strip=True) if title_tag else "Title not found"
    logger.debug("Extracted title: %s", title)

    # Find and remove the "More like this" section by locating the <b> tag
    more_like_this_section = soup.find('b', id="more-like-this:")
    if more_like_this_section:
        # Get the grandparent <div> that contains the whole section and remove it
        parent_section = more_like_this_section.find_parent('div')
        if parent_section:
            parent_section.decompose()
            logger.debug("Removed 'More like this' section.")

    # Find the main article tag
    article = soup.find('article')
    if article:
        content = []
        # Loop through each <p> tag within the article
        for paragraph in article.find_all('p'):
            # Remove any <u> tags within the paragraph
            for u_tag in paragraph.find_all('u'):
                u_tag.decompose()  # Remove <u> tag

            paragraph_text = paragraph.get_text(strip=True)
            content.append(paragraph_text)
            logger.debug("Extracted paragraph text: %s", paragraph_text)

        article_content = " ".join(content)
        logger.debug("Full article content extracted.")
        return article_content, title
    else:
        logger.warning("No article content found.")
        return None, title

@article_content_bp.route('/article', methods=['GET'])
def get_article_content():
    url = request.args.get('url')
    if not url:
        logger.error("No URL provided in the request.")
        return jsonify({'error': 'No URL provided'}), 400

    logger.debug("Received URL: %s", url)
    article_content, title = scrape_bbc(url)

    if article_content is None:
        logger.error("Article content extraction failed.")
        return jsonify({'error': 'Failed to extract article content'}), 500

    # Call OpenAI API to rewrite text in Spanish
    try:
        simplified_text = simplify_text(article_content)
        logger.debug("Simplified text generated successfully.")
    except Exception as e:
        logger.error("Error during text simplification: %s", e)
        return jsonify({'error': 'Failed to simplify text'}), 500

    content = {
        'title': title,
        'simplified_text': simplified_text,
    }

    logger.debug("Returning response with title and simplified text.")
    return jsonify(content)
