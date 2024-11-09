import logging
from openai import OpenAI
from flask import current_app
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the path to your resources directory
PROMPT_FILE_PATH = os.path.join(os.path.dirname(__file__), '../../resources/system_prompt.txt')


# Load the detailed system prompt from the file
with open(PROMPT_FILE_PATH, "r") as file:
    DETAILED_SYSTEM_PROMPT = file.read()

def simplify_text(text):
    # Log the start of the function
    logger.info("Starting translation process.")

    # Split the text into paragraphs
    paragraphs = text.split('\n')

    chunks = []
    current_chunk = ''
    current_chunk_word_count = 0
    chunk_size = 500

    for para in paragraphs:
        para_word_count = len(para.split())
        # Check if adding the current paragraph exceeds the chunk size
        if current_chunk_word_count + para_word_count > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = para + '\n'
            current_chunk_word_count = para_word_count
        else:
            current_chunk += para + '\n'
            current_chunk_word_count += para_word_count

    # Append any remaining text as the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    total_chunks = len(chunks)
    logger.info(f"Total chunks created: {total_chunks}")

    client = OpenAI()
    translated_chunks = []

    total_input_tokens = 0
    total_output_tokens = 0

    for idx, chunk in enumerate(chunks, start=1):
        logger.info(f"Translating chunk {idx}/{total_chunks}")

        prompt = chunk
        logger.debug(f"Prompt for chunk {idx}:\n{prompt}")

        # Estimate tokens for this chunk
        system_message_tokens = 8  # Approximate tokens for system message
        prompt_tokens = 12 + int(len(chunk.split()) * 1.5)  # Approximate tokens for user message
        input_tokens = system_message_tokens + prompt_tokens
        total_input_tokens += input_tokens
        logger.debug(f"Estimated input tokens for chunk {idx}: {input_tokens}")

        # Make the API call
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": DETAILED_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )
            translated_text = completion.choices[0].message.content.strip()
            translated_chunks.append(translated_text)
            logger.info(f"Chunk {idx} translated successfully.")
            print(translated_text)


            # Estimate output tokens for this chunk
            output_tokens = int(len(translated_text.split()) * 1.5)  # Approximate
            total_output_tokens += output_tokens
            logger.debug(f"Estimated output tokens for chunk {idx}: {output_tokens}")

        except Exception as e:
            logger.error(f"Error translating chunk {idx}: {e}")
            # Optionally handle the error, e.g., retry or skip

    # Calculate cost
    input_token_cost = (total_input_tokens / 1_000_000) * 0.150
    output_token_cost = (total_output_tokens / 1_000_000) * 0.600
    total_cost = input_token_cost + output_token_cost
    logger.info(f"Estimated total input tokens: {total_input_tokens}")
    logger.info(f"Estimated total output tokens: {total_output_tokens}")
    logger.info(f"Estimated Cost: ${total_cost:.6f}")

    # Combine the translated chunks
    full_translated_text = ' '.join(translated_chunks)
    logger.info("Translation process completed.")
    return full_translated_text