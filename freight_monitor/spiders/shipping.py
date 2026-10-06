"""
Shipping spider for NEW_PROJECT_NAME project.

Demonstrates the complete Scrapy workflow for shipping quote extraction.
Uses mock data to validate architecture without requiring external API credentials.

This spider can be replaced with real implementations (Correios, Jadlog, etc.)
while maintaining the same interface and output format.
"""

import hashlib
import json
import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst


class ShippingQuoteItem(scrapy.Item):
    """Normalized shipping quote item."""
    provider = scrapy.Field()
    service = scrapy.Field()
    price = scrapy.Field()
    delivery_time = scrapy.Field()
    currency = scrapy.Field()
    available = scrapy.Field()
    tracking_number = scrapy.Field()


class ShippingSpider(scrapy.Spider):
    """Base shipping spider demonstrating the complete workflow."""

    name = "shipping"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com"]

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
    }

    def __init__(self, origin_cep=None, dest_cep=None, weight=None,
                 service_code=None, **kwargs):
        super().__init__(**kwargs)
        self.origin_cep = origin_cep
        self.dest_cep = dest_cep
        self.weight = weight
        self.service_code = service_code

    def parse(self, response):
        """Parse response and return shipping quotes.

        This is the standard pattern all shipping spiders follow:
        1. Receive Response
        2. Extract raw data
        3. Normalize via ItemLoader
        4. Return ShippingQuoteItem(s)
        """
        self.logger.info("Processing shipping request: %s -> %s",
                        self.origin_cep, self.dest_cep)

        # For demonstration, use mock data based on inputs
        # In a real implementation, this would parse the API response
        quotes = self._get_mock_quotes()

        for quote in quotes:
            loader = ItemLoader(item=ShippingQuoteItem())
            loader.add_value("provider", quote.get("provider", "unknown"))
            loader.add_value("service", quote.get("service", "unknown"))
            loader.add_value("price", quote.get("price"))
            loader.add_value("delivery_time", quote.get("delivery_time"))
            loader.add_value("currency", quote.get("currency", "BRL"))
            loader.add_value("available", quote.get("available", True))
            loader.add_value("tracking_number", quote.get("tracking_number"))
            yield loader.load_item()

    def _get_mock_quotes(self):
        """Get mock shipping quotes based on package details.

        In a real implementation, this would parse the API response.
        Currently returns simulated data to validate the workflow.
        """
        # Build a deterministic mock based on CEPs and weight
        key = f"{self.origin_cep or '0'}-{self.dest_cep or '0'}-{self.weight or '0'}"
        h = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)

        # Two standard Brazilian shipping options
        services = [
            {
                "provider": "correios",
                "service": "SEDEX",
                "price": round(20.00 + (h % 15), 2),  # R$20-34
                "delivery_time": 3 + (h % 4),  # 3-6 days
                "currency": "BRL",
                "available": True,
                "tracking_number": f"SG{h % 1000000:06d}",
            },
            {
                "provider": "correios",
                "service": "PAC",
                "price": round(15.00 + (h % 12), 2),  # R$15-26
                "delivery_time": 5 + (h % 5),  # 5-9 days
                "currency": "BRL",
                "available": True,
                "tracking_number": f"AS{h % 1000000:06d}",
            },
        ]

        # Sometimes simulate unavailable service
        if h % 10 > 7:
            services.append({
                "provider": "correios",
                "service": "SEDEX 10",
                "price": None,
                "delivery_time": None,
                "currency": "BRL",
                "available": False,
                "tracking_number": None,
            })

        return services


# For direct execution: scrapy crawl shipping -a origin_cep=01001-000 -a dest_cep=09000-000 -a weight=650
