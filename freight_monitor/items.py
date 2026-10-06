# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import json
import scrapy
from itemloaders.processors import TakeFirst, MapCompose


class ShippingQuoteItem(scrapy.Item):
    """Normalized shipping quote item."""
    provider = scrapy.Field()
    service = scrapy.Field()
    price = scrapy.Field()
    delivery_time = scrapy.Field()
    currency = scrapy.Field()
    available = scrapy.Field()
    tracking_number = scrapy.Field()


def clean_price(value):
    """Clean and convert price string to float."""
    if value is None:
        return None
    value = str(value).replace("R$", "").strip()
    value = value.replace(".", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None


def clean_delivery_time(value):
    """Clean and convert delivery time to int or None."""
    if value is None:
        return None
    import re
    match = re.search(r"(\d+)", str(value))
    if match:
        return int(match.group(1))
    return None