# scrapy crawl third_party -a origin_cep=01001-000 -a dest_cep=09000-000 -a weight=650

"""
Third-party shipping spider for freight_monitor project.
"""

import scrapy


class ShippingQuoteItem(scrapy.Item):
    provider = scrapy.Field()
    service = scrapy.Field()
    price = scrapy.Field()
    delivery_time = scrapy.Field()
    currency = scrapy.Field()
    available = scrapy.Field()
    tracking_number = scrapy.Field()


class ThirdPartySpider(scrapy.Spider):
    name = "third_party"
    allowed_domains = ["example.com"]
    
    def __init__(self, origin_cep=None, dest_cep=None, weight=None, **kwargs):
        super().__init__(**kwargs)
        self.origin_cep = origin_cep or "01001-000"
        self.dest_cep = dest_cep or "09000-000"
        self.weight = weight or "650"
    
    def start_requests(self):
        # Mock spider - returns static data
        yield {
            "provider": "third_party",
            "service": "Express",
            "price": 25.00,
            "delivery_time": 2,
            "currency": "BRL",
            "available": True,
            "tracking_number": None,
        }
