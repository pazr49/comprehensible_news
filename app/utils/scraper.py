import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from app.models.article_element import ArticleElement

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def scrape_and_chunk_article(url, chunk_size):
    try:
        article_content, title, thumbnail = scrape_bbc(url)
        print("Article content: ", article_content)
        if article_content is None:
            logger.error("Article content extraction failed for %s", url)
            return None

        chunks = split_text_into_chunks(article_content, chunk_size)
        logger.info(f"Text chunking process completed successfully for {url}")
        return chunks, title, thumbnail
    except Exception as e:
        logger.exception("An error occurred while scraping and chunking the article: %s", e)
        return None

def scrape_bbc(url):
    logger.debug("Starting scrape_bbc function with URL: %s", url)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    if 'DYNO' in os.environ:
        chrome_binary_path = "/app/.chrome-for-testing/chrome-linux64/chrome"
        chromedriver_path = "/app/.chrome-for-testing/chromedriver-linux64/chromedriver"
        chrome_options.binary_location = chrome_binary_path
        service = Service(chromedriver_path)
    else:
        service = Service('C:/chromedriver/chromedriver.exe')

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'article')))
        page_source = driver.page_source
        logger.debug("Page retrieved successfully.")
    except Exception as e:
        logger.error("Error retrieving the page: %s", e)
        driver.quit()
        return None

    soup = BeautifulSoup(page_source, 'html.parser')
    driver.quit()

    title_tag = soup.find('div', {'data-component': 'headline-block'})
    title = title_tag.find('h1').get_text(strip=True) if title_tag else "Title not found"
    logger.debug("Extracted title: %s", title)

    more_like_this_section = soup.find('b', id="more-like-this:")
    if more_like_this_section:
        parent_section = more_like_this_section.find_parent('div')
        if parent_section:
            parent_section.decompose()
            logger.debug("Removed 'More like this' section.")

    article = soup.find('article')
    if not article:
        logger.warning("No article content found.")
        return None

    article_content = []
    thumbnail = ''
    for position, tag in enumerate(article.find_all(['p', 'figure', 'h2'])):
        if tag.name == 'figure':
            img_tag = tag.find('img')
            if img_tag and 'srcset' in img_tag.attrs:
                srcset = img_tag['srcset']
                image_url = srcset.split(',')[-1].split()[0]
                article_content.append(ArticleElement('image', image_url))
                logger.debug("Extracted image URL: %s", image_url)
                if not thumbnail:
                    thumbnail = image_url
                    logger.debug("Assigned thumbnail URL: %s", thumbnail)
        elif tag.name == 'p':
            for u_tag in tag.find_all('u'):
                u_tag.decompose()
            paragraph_text = tag.get_text(strip=True)
            article_content.append(ArticleElement('paragraph', paragraph_text))
            logger.debug("Extracted paragraph text: %s", paragraph_text)
        elif tag.name == 'h2':
            if tag.find_parent('div', {'data-component': 'links-block'}) is None:
                header_text = tag.get_text(strip=True)
                article_content.append(ArticleElement('header', header_text))
                logger.debug("Extracted header text: %s", header_text)

    logger.debug("Full article content extracted.")
    return article_content, title, thumbnail

def split_text_into_chunks(article_content, chunk_size):
    chunks = []
    current_chunk = ''
    current_chunk_word_count = 0

    logger.debug("Starting text chunking process.")
    for element in article_content:
        if element.type == 'image':
            if current_chunk.strip():
                chunks.append(ArticleElement('paragraph', current_chunk.strip()))
                current_chunk = ''
                current_chunk_word_count = 0
            chunks.append(element)
            continue
        if element.type == 'header':
            if current_chunk.strip():
                chunks.append(ArticleElement('paragraph', current_chunk.strip()))
                current_chunk = ''
                current_chunk_word_count = 0
            chunks.append(element)
            continue

        para_word_count = len(element.content.split())
        if current_chunk_word_count + para_word_count > chunk_size and current_chunk:
            chunks.append(ArticleElement('paragraph', current_chunk.strip()))
            current_chunk = element.content + '\n'
            current_chunk_word_count = para_word_count
        else:
            current_chunk += element.content + '\n'
            current_chunk_word_count += para_word_count

    if current_chunk.strip():
        chunks.append(ArticleElement('paragraph', current_chunk.strip()))

    total_chunks = len(chunks)
    logger.info(f"Total chunks created: {total_chunks}")
    return chunks

def estimate_tokens(text):
    return int(len(text.split()) * 1.5)