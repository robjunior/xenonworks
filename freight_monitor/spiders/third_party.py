"""
Third party shipping spider for freight_monitor project.

Demonstrates adding additional providers beyond the initial two (Correios + Jadlog).
All spiders must produce output conforming to the
freight_monitor.contracts.ShippingQuote contract.

This spider uses mock data to validate the multi-provider architecture
without requiring third-party API credentials.
"""

import hashlib
import scrapy
from freight_monitor.contracts import ShippingQuote


class ThirdPartySpider(scrapy.Spider):
    """Spider for querying third-party shipping rates."""

    name = "third_party"

    def __init__(self, origin_cep=None, dest_cep=None, weight=None,
                 service_code=None):
        self.origin_cep = origin_cep
        self.dest_cep = dest_cep
        self.weight = weight
        self.service_code = service_code

    def parse(self, response):
        """Parse the response and extract shipping quotes."""
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
        """Get mock third-party shipping quotes based on package details.

        In a real implementation, this would parse the API response.
        Currently returns simulated data to validate the multi-provider workflow.
        The quotes produced conform to the freight_monitor.contracts.ShippingQuote contract.
        """
        # Build a deterministic mock based on CEPs and weight
        key = f"{self.origin_cep or '0'}-{self.dest_cep or '0'}-{self.weight or '0'}"
        h = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)

        # Third party offers different services
        quotes = [
            {
                "provider": "third_party",
                "service": "Third Party Express",
                "price": round(18.00 + (h % 10), 2),  # R$18-27
                "delivery_time": 3 + (h % 4),  # 3-6 days
                "currency": "BRL",
                "available": True,
                "tracking_number": f"T{h % 1000000:06d}",
            },
            {
                "provider": "third_party",
                "service": "Third Party Economy",
                "price": round(15.00 + (h % 8), 2),  # R$15-22
                "delivery_time": 5 + (h % 5),  # 5-9 days
                "currency": "BRL",
                "available": (h % 10) != 0,  # 90% availability
                "tracking_number": f"E{h % 1000000:06d}",
            },
        ]

        # Sometimes simulate unavailable service
        if h % 20 > 15:
            quotes.append({
                "provider": "third_party",
                "service": "Third Party Premium",
                "price": None,
                "delivery_time": None,
                "currency": "BRL",
                "available": False,
                "tracking_number": None,
            })

        return quotes


# For direct integration: add ThirdPartySpider to aggregator providers list
