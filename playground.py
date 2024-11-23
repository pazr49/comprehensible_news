import json
import logging
import random
import string


def do_stuff():
    article_id = f"article_group_{''.join(random.choices(string.ascii_lowercase + string.digits, k=12))}"
    print(article_id)

for i in range(5):
    do_stuff()
