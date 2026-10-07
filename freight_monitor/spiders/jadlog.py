# scrapy crawl jadlog -a origin_cep=01001-000 -a dest_cep=09000-000 -a weight=650

"""
Jadlog shipping spider for freight_monitor project.
"""

import json
import re
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


def clean_price(value):
    if value is None:
        return None
    value = str(value).replace("R$", "").strip()
    value = value.replace(".", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None


def clean_delivery_time(value):
    if value is None:
        return None
    match = re.search(r"(\d+)", str(value))
    if match:
        return int(match.group(1))
    return None


class JadlogSpider(scrapy.Spider):
    """Spider for querying Jadlog shipping rates."""
    
    name = "jadlog"
    allowed_domains = ["jadlog.com.br"]
    
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }
    
    def __init__(self, origin_cep=None, dest_cep=None, weight=None, **kwargs):
        super().__init__(**kwargs)
        # Use defaults for discovery
        self.origin_cep = origin_cep or "01001-000"
        self.dest_cep = dest_cep or "09000-000"
        self.weight = weight or "650"
    
    def start_requests(self):
        # Mock endpoint for Jadlog
        url = "https://api.jadlog.com.br/cotacao"
        
        formdata = {
            "cepOrigem": self.origin_cep.replace("-", ""),
            "cepDestino": self.dest_cep.replace("-", ""),
            "peso": str(self.weight),
        }
        
        yield scrapy.FormRequest(
            url=url,
            formdata=formdata,
            callback=self.parse,
            errback=self.handle_error,
        )
    
    def parse(self, response):
        # Mock parsing - returns sample data
        mock_quotes = [
            {
                "provider": "jadlog",
                "service": "Jadlog Express",
                "price": "33.00",
                "delivery_time": "3",
                "currency": "BRL",
                "available": True,
                "tracking_number": "JD123456",
            },
            {
                "provider": "jadlog",
                "service": "Jadlog Priority",
                "price": "29.00",
                "delivery_time": "5",
                "currency": "BRL",
                "available": True,
                "tracking_number": "JD789012",
            },
        ]
        
        for quote in mock_quotes:
            yield {
                "provider": quote["provider"],
                "service": quote["service"],
                "price": clean_price(quote["price"]),
                "delivery_time": clean_delivery_time(quote["delivery_time"]),
                "currency": quote["currency"],
                "available": quote["available"],
                "tracking_number": quote["tracking_number"],
            }
    
    def handle_error(self, failure):
        self.logger.error("Error requesting Jadlog: %s", failure.value)
        yield {
            "provider": "jadlog",
            "service": "ERROR",
            "price": None,
            "delivery_time": None,
            "currency": "BRL",
            "available": False,
            "tracking_number": None,
            "_error": str(failure.value),
        }
