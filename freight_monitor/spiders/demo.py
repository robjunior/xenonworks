"""
Demonstration spider for NEW_PROJECT_NAME project.

This spider demonstrates the Scrapy architecture for the shipping monitor project.
It uses a simple example website to show the pattern of:
- Request generation
- Response parsing  
- Item loading/normalization
- Error handling
"""

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose


class ShippingQuoteItem(scrapy.Item):
    """Normalized shipping quote item."""
    provider = scrapy.Field()
    service = scrapy.Field()
    price = scrapy.Field()
    delivery_time = scrapy.Field()
    currency = scrapy.Field()
    available = scrapy.Field()


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
    match = __import__("re").search(r"(\d+)", str(value))
    if match:
        return int(match.group(1))
    return None


class DemoSpider(scrapy.Spider):
    """Demo spider for architecture validation."""

    name = "demo"
    allowed_domains = ["httpbin.org"]
    start_urls = ["https://httpbin.org/get"]

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "FEED_FORMAT": "json",
    }

    def parse(self, response):
        """Parse the demo response and extract shipping-relevant data."""
        self.logger.info("Received response from %s", response.url)

        # httpbin.org returns JSON - parse it
        import json
        data = json.loads(response.text)

        # Extract some data from the JSON response
        loader = ItemLoader(item=ShippingQuoteItem())

        loader.add_value("provider", "demo")
        loader.add_value("service", "httpbin-example")
        # Extract URL from the JSON response
        loader.add_value("price", clean_price(
            data.json.get("url", "")
        ))
        loader.add_value("delivery_time", clean_delivery_time(
            str(data.json.get("args", {}).get("arg_url", ""))
        ))
        loader.add_value("currency", "BRL")
        loader.add_value("available", True)
        loader.add_value("tracking_number", None)

        yield loader.load_item()


# For direct execution: scrapy crawl demo