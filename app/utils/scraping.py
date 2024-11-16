from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import logging
import os

from app.models.article_element import ArticleElement

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def scrape_bbc(url):
    logger.debug("Starting scrape_bbc function with URL: %s", url)

    # Set up Selenium with ChromeDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    if 'DYNO' in os.environ:  # Check if running on Heroku
        chrome_options.binary_location = "/app/.apt/usr/bin/google-chrome"
        service = Service("/app/.apt/usr/bin/chromedriver")
    else:
        service = Service('C:/chromedriver/chromedriver.exe')
        # Update with the path to your ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'article')))
        page_source = driver.page_source
    except Exception as e:
        logger.error("Error retrieving the page: %s", e)
        driver.quit()
        return None, None

    logger.debug("Page retrieved successfully.")

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extract the title from the headline block
    title_tag = soup.find('div', {'data-component': 'headline-block'})
    title = title_tag.find('h1').get_text(strip=True) if title_tag else "Title not found"
    logger.debug("Extracted title: %s", title)

    # Find and remove the "More like this" section by locating the <b> tag
    more_like_this_section = soup.find('b', id="more-like-this:")
    if more_like_this_section:
        # Get the grandparent <div> that contains the whole section and remove it
        parent_section = more_like_this_section.find_parent('div')
        if (parent_section):
            parent_section.decompose()
            logger.debug("Removed 'More like this' section.")

    # Find the main article tag
    article = soup.find('article')
    if article:
        article_content = []
        # Loop through each <p> and <figure> tag within the article
        for position, tag in enumerate(article.find_all(['p', 'figure'])):
            if tag.name == 'figure':
                img_tag = tag.find('img')
                if img_tag:
                    logger.debug("Found img tag: %s", img_tag)
                    if 'srcset' in img_tag.attrs:
                        logger.debug("Found srcset attribute in img tag: %s", img_tag['srcset'])
                        # Extract the highest resolution image URL from the srcset attribute
                        srcset = img_tag['srcset']
                        image_url = srcset.split(',')[-1].split()[0]
                        article_element = ArticleElement('image', image_url)
                        article_content.append(article_element)
                        logger.debug("Extracted image URL: %s", image_url)
                    else:
                        logger.debug("srcset attribute not found in img tag.")
                else:
                    logger.debug("img tag not found.")

            if tag.name == 'p':
                for u_tag in tag.find_all('u'):
                    u_tag.decompose()  # Remove <u> tag
                paragraph_text = tag.get_text(strip=True)
                article_element = ArticleElement('paragraph', paragraph_text)
                article_content.append(article_element)
                logger.debug("Extracted tag text: %s", paragraph_text)

        logger.debug("Full article content extracted.")
        driver.quit()
        print(article_content)
        return article_content, title
    else:
        logger.warning("No article content found.")
        driver.quit()
        return None, title