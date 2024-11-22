import json


from app.utils.bbc_rss_reader import bbc_rss_reader
from app.utils.scraper import scrape_and_chunk_article
from app.utils.simplifier import simplify_article
from app.utils.translator import translate_article


def do_stuff():

    rss_feed = bbc_rss_reader("news", 1)

    for rss_article in rss_feed:
        chunked_article = scrape_and_chunk_article(rss_article)

        simplified_article, total_input_tokens, total_output_tokens = simplify_article(rss_article, chunked_article, "A1")

        translated_article, total_input_tokens, total_output_tokens = translate_article(simplified_article, "es", "A1")

        print("Translated article:", translated_article)
        return

do_stuff()
