import requests
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        article_content = []
        # Loop through each <p> and <figure> tag within the article
        for position, element in enumerate(article.find_all(['p', 'figure'])):
            # Remove any <u> tags within the element

            if element.name == 'figure':
                img_tag = element.find('img')
                if img_tag:
                    logger.debug("Found img tag: %s", img_tag)
                    if 'srcset' in img_tag.attrs:
                        logger.debug("Found srcset attribute in img tag: %s", img_tag['srcset'])
                        # Extract the highest resolution image URL from the srcset attribute
                        srcset = img_tag['srcset']
                        image_url = srcset.split(',')[-1].split()[0]
                        article_content.append({
                            'position': position,
                            'type': 'image',
                            'content': image_url
                        })
                        logger.debug("Extracted image URL: %s", image_url)
                    else:
                        print("srcset attribute not found in img tag.")
                        logger.debug("srcset attribute not found in img tag.")
                else:
                    logger.debug("img tag not found.")

            if element.name == 'p':
                for u_tag in element.find_all('u'):
                    u_tag.decompose()  # Remove <u> tag
                paragraph_text = element.get_text(strip=True)
                article_content.append(
                    {
                        'position': position,
                        'type': 'paragraph',
                        'content': paragraph_text
                    }
                )
                logger.debug("Extracted element text: %s", paragraph_text)


        logger.debug("Full article content extracted.")
        print(article_content)
        return article_content, title
    else:
        logger.warning("No article content found.")
        return None, title