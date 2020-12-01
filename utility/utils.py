
from random import choice
from uuid import uuid1

from notion.client import NotionClient

from utility.logs import setup_log

logger = setup_log(module_name=__name__, log_level="DEBUG")

colors = [
    "default",
    "gray",
    "brown",
    "orange",
    "yellow",
    "green",
    "blue",
    "purple",
    "pink",
    "red",
]


def _find_prop_schema(schema, prop):
    return next((v for k, v in schema.items() if v["name"] == prop), None)


def _add_new_multi_select_value(collection, schema, prop, value, color=None):
    if color is None:
        color = choice(colors)

    prop_schema = _find_prop_schema(schema, prop)
    if not prop_schema:
        logger.critical(f'"{prop}" property does not exist on the collection!')
        raise ValueError(
            f'"{prop}" property does not exist on the collection!'
        )

    if prop_schema["type"] != "multi_select":
        raise ValueError(f'"{prop}" is not a multi select property!')

    dupe = next(
        (o for o in prop_schema["options"] if o["value"] == value), None
    )
    if not dupe:

        prop_schema["options"].append(
            {"id": str(uuid1()), "value": value, "color": color}
        )
        try:
            collection.set("schema", schema)
        except (RecursionError, UnicodeEncodeError) as e:
            # Catch `RecursionError` and `UnicodeEncodeError`
            # in `notion-py/store.py/run_local_operation`,
            # because I've no idea why does it raise an error.
            # The schema is correctly updated on remote.
            logger.critical(f"RecursionError, UnicodeEncodeError - {e}")
            pass
    else:
        logger.warning(f'"{value}" already exists in the schema!')
        # raise ValueError(f'"{value}" already exists in the schema!')


def _set_multi_select_property(collection, page, schema, prop, new_values):
    new_values_set = set(new_values)
    current_options_set = set(
        [o["value"] for o in _find_prop_schema(schema, prop)["options"]]
    )
    intersection = new_values_set.intersection(current_options_set)
    if len(new_values_set) > len(intersection):
        difference = [v for v in new_values_set if v not in intersection]
        for d in difference:
            _add_new_multi_select_value(collection, schema, prop, d)
    page.set_property(prop, new_values)


def get_notion(token_v2, page_link):
    # Obtain the `token_v2` value by inspecting your browser cookies on a logged-in (non-guest) session on Notion.so
    client = NotionClient(token_v2=token_v2)

    # Access a database using the URL of the database page or the inline block
    collection_view = client.get_collection_view(page_link)
    collection = collection_view.collection
    return collection, collection_view


def extract_element(collection, item_list, key, value, column):
    elem_list = []
    for item_id in item_list:
        if item_id in item_list:
            item = item_list[item_id]
            if key in item:
                for el_id in item[key]:
                    element = item[key][el_id][value]
                    _add_new_multi_select_value(collection=collection,
                                                schema=collection.get("schema"),
                                                prop=column,
                                                value=element)
                    elem_list.append(element)
            else:
                logger.warning("Element has no tags")
        else:
            logger.warning("Element does not exist in list")

    return list(dict.fromkeys((elem_list)))
