import logging
from openai import OpenAI
import os
from app.utils import estimate_tokens
import pycountry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

levels = ['A1', 'A2', 'B1', 'B2', 'C1']


prompts = {}
for level in levels:
    PROMPT_FILE_PATH = os.path.join(os.path.dirname(__file__), f'../../resources/simplify_system_prompt_{level}.txt')
    with open(PROMPT_FILE_PATH, "r") as file:
        prompts[level] = file.read()

# Takes a text input and simplifies the language using the GPT-4o-mini model
def open_ai_simplify_text(text, target_level):
    logger.info("Starting openai simplifying process.")

    client = OpenAI()

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompts[target_level]},
                {"role": "user", "content": text}
            ]
        )
        simplified_text = completion.choices[0].message.content.strip()

        total_input_tokens = estimate_tokens(text)
        total_output_tokens = estimate_tokens(simplified_text)

        logger.info("Simplification process completed successfully.")
        logger.info(f"Input tokens: {total_input_tokens}, Output tokens: {total_output_tokens}")
        return simplified_text, total_input_tokens, total_output_tokens

    except Exception as e:
        logger.error(f"Error in simplifying text")


def open_ai_translate_text(text, target_language, target_level):
    logger.info("Starting translation process.")

    client = OpenAI()

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Translate the following text into {target_language}. Keep in mind this is for "
                                              f"an {target_level} level {target_language} learner so try to avoid using complex "
                                              f"word translations, but do aim to translate as close to the original as possible: "},
                {"role": "user", "content": text}
            ]
        )
        translated_text = completion.choices[0].message.content.strip()

        total_input_tokens = estimate_tokens(text)
        total_output_tokens = estimate_tokens(translated_text)

        logger.info("Text translated successfully.")
        logger.info(f"Input tokens: {total_input_tokens}, Output tokens: {total_output_tokens}")
        return translated_text, total_input_tokens, total_output_tokens
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        return None, None, None