"""
Jadlog shipping spider for freight_monitor project.

Demonstrates multi-provider support following the same interface as
the Correios spider. All spiders must produce output conforming to
the freight_monitor.contracts.ShippingQuote contract.

This spider uses mock data to validate the architecture without
requiring Jadlog API credentials.
"""

import hashlib
import json
import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst

from freight_monitor.contracts import ShippingQuote


class JadlogQuoteItem(scrapy.Item):
    """Internal Scrapy item for Jadlog spider."""
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
    import re
    match = re.search(r"(\d+)", str(value))
    if match:
        return int(match.group(1))
    return None


class JadlogSpider(scrapy.Spider):
    """Spider for querying Jadlog shipping rates."""

    name = "jadlog"
    allowed_domains = ["jadlog.com.br"]
    start_urls = ["https://jadlog.com.br"]  # Fallback, overridden by start_requests

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }

    def __init__(self, origin_cep=None, dest_cep=None, weight=None,
                 service_code=None, **kwargs):
        super().__init__(**kwargs)
        self.origin_cep = origin_cep
        self.dest_cep = dest_cep
        self.weight = weight
        self.service_code = service_code

    def start_requests(self):
        """Generate request - Jadlog uses mock data, no real API call needed."""
        # For demonstration, we yield a mock request that triggers the
        # parse method with mock data. In a real implementation, this
        # would make an actual API request to Jadlog.
        self.logger.info("Jadlog spider: using mock data (no real API call)")

        # Yield a simple request that will trigger parse with mock data
        # The parse method uses _get_mock_quotes() to generate data
        yield {
            "mock": True,
            "origin_cep": self.origin_cep,
            "dest_cep": self.dest_cep,
            "weight": self.weight,
        }

    def parse(self, response):
        """Parse the Jadlog response and extract shipping quotes.

        This is the standard pattern all shipping spiders follow:
        1. Receive Response (or mock data)
        2. Extract raw data (mock or API)
        3. Normalize via ItemLoader -> JadlogQuoteItem
        4. Also yield ShippingQuote contract entity
        5. Return JadlogQuoteItem(s)
        """
        self.logger.info("Processing Jadlog request: %s -> %s",
                        self.origin_cep, self.dest_cep)

        # Check if this is a mock request
        if response.url.endswith("jadlog.com.br"):
            # Real website - would parse actual response
            # For now, use mock data
            quotes = self._get_mock_quotes()
        else:
            # Mock request - response will be minimal
            quotes = self._get_mock_quotes()

        for quote_dict in quotes:
            # Convert dict to ShippingQuote contract entity
            quote = ShippingQuote(
                provider=quote_dict.get("provider", "unknown"),
                service=quote_dict.get("service", "unknown"),
                price=quote_dict.get("price"),
                delivery_time=quote_dict.get("delivery_time"),
                currency=quote_dict.get("currency", "BRL"),
                available=quote_dict.get("available", True),
                tracking_number=quote_dict.get("tracking_number"),
            )

            # Also yield the Scrapy Item for framework compatibility
            loader = ItemLoader(item=JadlogQuoteItem())
            loader.add_value("provider", quote.provider)
            loader.add_value("service", quote.service)
            loader.add_value("price", quote.price)
            loader.add_value("delivery_time", quote.delivery_time)
            loader.add_value("currency", quote.currency)
            loader.add_value("available", quote.available)
            loader.add_value("tracking_number", quote.tracking_number)
            yield loader.load_item()
            yield quote

    def _get_mock_quotes(self):
        """Get mock Jadlog shipping quotes based on package details.

        In a real implementation, this would parse the Jadlog API response.
        Currently returns simulated data to validate the multi-provider workflow.
        The quotes produced conform to the freight_monitor.contracts.ShippingQuote contract.
        """
        # Build a deterministic mock based on CEPs and weight
        key = f"{self.origin_cep or '0'}-{self.dest_cep or '0'}-{self.weight or '0'}"
        h = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)

        # Jadlog typically offers similar services to Correios
        quotes = [
            {
                "provider": "jadlog",
                "service": "Jadlog Express",
                "price": round(22.00 + (h % 13), 2),  # R$22-34
                "delivery_time": 2 + (h % 5),  # 2-6 days
                "currency": "BRL",
                "available": True,
                "tracking_number": f"J{h % 1000000:06d}",
            },
            {
                "provider": "jadlog",
                "service": "Jadlog Priority",
                "price": round(28.00 + (h % 10), 2),  # R$28-37
                "delivery_time": 1 + (h % 3),  # 1-3 days
                "currency": "BRL",
                "available": True,
                "tracking_number": f"P{h % 1000000:06d}",
            },
        ]

        # Sometimes simulate unavailable service
        if h % 10 > 8:
            quotes.append({
                "provider": "jadlog",
                "service": "Jadlog Flex",
                "price": None,
                "delivery_time": None,
                "currency": "BRL",
                "available": False,
                "tracking_number": None,
            })

        return quotes


# For direct execution: scrapy crawl jadlog -a origin_cep=01001-000 -a dest_cep=09000-000 -a weight=650
