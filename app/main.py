# import json
from os import environ

import chromedriver_binary
from selenium import webdriver

from utility.getPocket import Pocket
from utility.logs import setup_log
from utility.utils import (_add_new_multi_select_value, extract_element,
                           get_notion)

# from .utils import _set_multi_select_property, get_notion

logger = setup_log(module_name=__name__, log_level="DEBUG")

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("window-size=1024,768")
chrome_options.add_argument("--no-sandbox")

# Initialize a new browser
browser = webdriver.Chrome(chrome_options=chrome_options)


def handle_row(row, data):
    try:
        row.name = data['resolved_title'] if 'resolved_title' in data else None
        row.excerpt = data['excerpt'] if 'excerpt' in data else None
        row.image = data['top_image_url'] if 'top_image_url' in data else ''
        row.lang = data['lang'] if 'lang' in data else None
        row.time_to_read = int(data['time_to_read']) if 'time_to_read' in data else None
        # row.title = "Just some data"
        row.unique_id = data['resolved_id'] if 'resolve_id' in data else None
        row.url = data['resolved_url'] if 'resolved_url' in data else None
        row.word_count = int(data['word_count']) if 'word_count' in data else None

        tags = []
        if 'tags' in data:
            for tag in data['tags']:
                tags.append(tag)
            row.tags = tags
        authors = []
        if 'authors' in data:
            for author_id in data['authors']:
                author = data['authors'][author_id]['name']
                authors.append(author)
            row.authors = authors

        return True

    except Exception as e:
        logger.critical(f"Error adding row {data['resolved_id']} - {data['resolved_title']} - {e}")
        return False


def add_row(collection, notion_view, data):
    try:
        # schema = collection.get("schema")
        row = notion_view.collection.add_row()
        return handle_row(row=row, data=data)
    except Exception as e:
        logger.critical(f"add_row Error adding row {data['resolved_id']} - {data['resolved_title']} - {e}")
        return False


def edit_row(collection, row, data):
    # schema = collection.get("schema")
    return handle_row(row=row, data=data)


def main():

    API_KEY = environ.get("API_KEY", "")
    USR = environ.get("USR", "")
    PSW = environ.get("PSW", "")

    token_v2 = environ.get("TOKEN_V2", "")
    page_link = environ.get("NOTION_LINK", "")

    if not API_KEY or not USR or not PSW or not token_v2 or not page_link:
        logger.critical("missing envar")
        exit()

    pocket = Pocket(consumer_key=API_KEY, user_email=USR, password=PSW, browser=browser)
    items = pocket.get_items(count=300, state='unread')

    if not items:
        logger.critical("Error getting items from pocket")
        raise LookupError("Error getting items from pocket")

    item_list = items['list']
    if item_list:
        collection, collection_view = get_notion(token_v2=token_v2, page_link=page_link)

        item_ids = []

        extract_element(collection=collection,
                        item_list=item_list,
                        key='authors',
                        value='name',
                        column='Authors')

        extract_element(collection=collection,
                        item_list=item_list,
                        key='tags',
                        value='tag',
                        column='Tags')

        lang = list(dict.fromkeys(([item_list[c]['lang'] for c in item_list])))
        for value in lang:
            _add_new_multi_select_value(collection=collection,
                                        schema=collection.get("schema"),
                                        prop='Lang',
                                        value=value)
        for item_id in item_list:
            item = item_list[item_id]
            filter_params = {
                "operator": "and",
                "filters": [
                    {
                        "property": "unique_id",
                        "filter": {
                            "operator": "string_is",
                            "value": {
                                "type": "exact",
                                "value": f"{item_id}"
                            }
                        }
                    }
                ]
            }
            result = collection_view.build_query(filter=filter_params).execute()
            # row = collection.get_rows(search=item_id)
            status = True
            if result:
                logger.info("the link exists, skipping")
                # row = result[0]
                # status = edit_row(collection=collection, row=row, data=item)
            else:
                status = add_row(collection=collection, notion_view=collection_view, data=item)
                logger.info(f"added - {item['resolved_id']}")
            # Add a new record
            if status:
                item_ids.append(item_id)

        pocket.set_items_archive(item_ids=item_ids)
        logger.info(f"END - total new links: {len(item_list)}")
    else:
        logger.info("No link to import")


if __name__ == '__main__':
    main()
