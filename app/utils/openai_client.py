import logging

from openai import OpenAI
import os
from app.utils.text_chuncking import estimate_tokens

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROMPT_FILE_PATH = os.path.join(os.path.dirname(__file__), '../../resources/system_prompt.txt')

with open(PROMPT_FILE_PATH, "r") as file:
    DETAILED_SYSTEM_PROMPT = file.read()

# Takes a text input and simplifies the language using the GPT-4o-mini model
def simplify_text(text):
    logger.info("Starting simplifying process.")

    client = OpenAI()

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": DETAILED_SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ]
        )
        simplified_text = completion.choices[0].message.content.strip()

        total_input_tokens = estimate_tokens(text)
        total_output_tokens = estimate_tokens(simplified_text)

        logger.info("Translation process completed successfully.")
        logger.info(f"Input tokens: {total_input_tokens}, Output tokens: {total_output_tokens}")
        return simplified_text, total_input_tokens, total_output_tokens

    except Exception as e:
        logger.error(f"Error simplifying text")


def translate_text(text, target_language):
    logger.info("Starting translation process.")

    client = OpenAI()

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Translate the following text into {target_language}"},
                {"role": "user", "content": text}
            ]
        )
        translated_text = completion.choices[0].message.content.strip()
        logger.info("Text translated successfully.")
        return translated_text
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        return None