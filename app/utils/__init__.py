import logging
# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def estimate_tokens(text):
    return int(len(text.split()) * 1.5)