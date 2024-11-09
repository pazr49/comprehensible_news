import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def split_text_into_chunks(text, chunk_size=500):
    paragraphs = text.split('\n')
    chunks = []
    current_chunk = ''
    current_chunk_word_count = 0

    for para in paragraphs:
        para_word_count = len(para.split())
        if current_chunk_word_count + para_word_count > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = para + '\n'
            current_chunk_word_count = para_word_count
        else:
            current_chunk += para + '\n'
            current_chunk_word_count += para_word_count

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    total_chunks = len(chunks)
    logger.info(f"Total chunks created: {total_chunks}")
    return chunks

def estimate_tokens(text):
    return int(len(text.split()) * 1.5)