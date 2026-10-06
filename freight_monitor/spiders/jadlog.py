"""
Jadlog shipping spider for freight_monitor project.

Demonstrates multi-provider support following the same interface as
the Correios spider. All spiders must produce output conforming to
the freight_monitor.contracts.ShippingQuote contract.

This spider uses mock data to validate the architecture without
requiring Jadlog API credentials.
"""

import hashlib
import scrapy

from freight_monitor.contracts import ShippingQuote


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
        self.logger.info("Jadlog spider: using mock data (no real API call)")

        # Yield a request that will trigger parse with mock data
        # In a real implementation, this would make an actual API request to Jadlog
        url = self.start_urls[0] if self.start_urls else "https://jadlog.com.br"
        yield scrapy.Request(
            url=url,
            callback=self.parse,
            meta={
                "origin_cep": self.origin_cep,
                "dest_cep": self.dest_cep,
                "weight": self.weight,
            },
            dont_filter=True,
        )

    def parse(self, response):
        """Parse the Jadlog response and extract shipping quotes.

        This is the standard pattern all shipping spiders follow:
        1. Receive Response (or mock data)
        2. Extract raw data (mock or API)
        3. Yield ShippingQuote contract entities
        """
        self.logger.info("Processing Jadlog request: %s -> %s",
                        self.origin_cep, self.dest_cep)

        # Use mock data - in real implementation would parse API response
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