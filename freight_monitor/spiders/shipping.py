# scrapy crawl shipping -a origin_cep=01001-000 -a dest_cep=09000-000 -a weight=650

"""
Alternative Correios shipping spider for freight_monitor project.
"""

import json
import re
import scrapy
from scrapy.loader import ItemLoader


class ShippingQuoteItem(scrapy.Item):
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


class ShippingSpider(scrapy.Spider):
    name = "shipping"
    allowed_domains = ["correios.com.br"]
    
    def __init__(self, origin_cep=None, dest_cep=None, weight=None, **kwargs):
        super().__init__(**kwargs)
        self.origin_cep = origin_cep or "01001-000"
        self.dest_cep = dest_cep or "09000-000"
        self.weight = weight or "650"
    
    def start_requests(self):
        url = "https://www.correios.com.br/calculador"
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
        # Mock implementation
        yield {
            "provider": "correios",
            "service": "SEDEX",
            "price": 31.00,
            "delivery_time": 6,
            "currency": "BRL",
            "available": True,
            "tracking_number": None,
        }
    
    def handle_error(self, failure):
        yield {
            "provider": "correios",
            "service": "ERROR",
            "available": False,
            "_error": str(failure.value),
        }
