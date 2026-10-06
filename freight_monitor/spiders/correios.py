# scrapy crawl correios -a origin_cep=01001-000 -a dest_cep=09000-000 -a weight=650 -a width=20 -a height=15 -a depth=10

"""
Correios shipping spider for NEW_PROJECT_NAME project.

This spider queries Correios web interface to obtain shipping quotes
based on origin/destination ZIP codes, weight, and dimensions.

Contract:
  ShippingRequest -> ShippingQuote[]

Input (via command line arguments):
  - origin_cep: Origin ZIP code (e.g., "01001-000")
  - dest_cep: Destination ZIP code (e.g., "09000-000")
  - weight: Package weight in grams
  - width: Width in centimeters
  - height: Height in centimeters
  - depth: Depth in centimeters

Output:
  List of ShippingQuote dicts with fields:
  - provider: "correios"
  - service: service name (e.g., "PAC", "SEDEX")
  - price: price in BRL (float)
  - delivery_time: estimated delivery time in days (int or None)
  - currency: "BRL"
  - available: boolean indicating if service is available
  - tracking_number: tracking code if available
  - raw_html: original response for debugging
"""

import json
import re
import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags


class ShippingQuoteItem(scrapy.Item):
    """Normalized shipping quote item."""
    provider = scrapy.Field()
    service = scrapy.Field()
    price = scrapy.Field()
    delivery_time = scrapy.Field()
    currency = scrapy.Field()
    available = scrapy.Field()
    tracking_number = scrapy.Field()
    raw_html = scrapy.Field()


def clean_price(value):
    """Clean and convert price string to float."""
    if value is None:
        return None
    # Remove R$, whitespace, and replace comma with dot
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
    # Extract number from strings like "3 dias", "5-7 dias", etc.
    match = re.search(r"(\d+)", str(value))
    if match:
        return int(match.group(1))
    return None


class CorreiosSpider(scrapy.Spider):
    """Spider for querying Correios shipping rates."""
    
    name = "correios"
    allowed_domains = ["correios.com.br"]
    
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }
    
    def __init__(self, origin_cep=None, dest_cep=None, weight=None, 
                 width=None, height=None, depth=None, **kwargs):
        super().__init__(**kwargs)
        self.origin_cep = origin_cep
        self.dest_cep = dest_cep
        self.weight = weight
        self.width = width
        self.height = height
        self.depth = depth
        
        # Validate required parameters
        if not all([origin_cep, dest_cep, weight]):
            raise ValueError(
                "Missing required parameters: origin_cep, dest_cep, weight"
            )
    
    def start_requests(self):
        """Generate the initial request to Correios."""
        # Build the Correios consultation URL
        url = "https://www.correios.com.br/sistema-web-tarifario/"
        
        # Prepare form data
        formdata = {
            "cepOrigem": self.origin_cep.replace("-", ""),
            "cepDestino": self.dest_cep.replace("-", ""),
            "peso": str(self.weight),
            "largura": str(self.width or 20),
            "altura": str(self.height or 15),
            "profundidade": str(self.depth or 10),
        }
        
        yield scrapy.FormRequest(
            url=url,
            formdata=formdata,
            callback=self.parse,
            errback=self.handle_error,
            meta={
                "origin_cep": self.origin_cep,
                "dest_cep": self.dest_cep,
                "weight": self.weight,
            }
        )
    
    def parse(self, response):
        """Parse the Correios response and extract shipping quotes."""
        # Save raw HTML for debugging
        import os
        import json
        debug_dir = os.path.join(os.path.dirname(__file__), "..", "debug")
        os.makedirs(debug_dir, exist_ok=True)
        debug_file = os.path.join(debug_dir, f"correios_{response.meta.get('origin_cep', 'unknown')}_{response.meta.get('dest_cep', 'unknown')}.html")
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        self.logger.info(
            "Saved raw HTML to %s (length: %d chars)",
            debug_file, len(response.text)
        )
        
        # Store raw HTML for debugging
        raw_html = response.text
        
        # Try to extract quote data from the response
        quotes = self._extract_quotes(response)
        
        for quote in quotes:
            loader = ItemLoader(item=ShippingQuoteItem(), selector=quote)
            loader.add_value("provider", "correios")
            loader.add_value("price", clean_price(
                quote.get("price") or quote.get("valor")
            ))
            loader.add_value("service", quote.get("service") or quote.get("nome"))
            loader.add_value("delivery_time", clean_delivery_time(
                quote.get("prazo_entrega") or quote.get("prazo")
            ))
            loader.add_value("currency", "BRL")
            loader.add_value("available", quote.get("disponivel", False))
            loader.add_value("tracking_number", quote.get("numero_rastreio"))
            loader.add_value("raw_html", raw_html)
            yield loader.load_item()
    
    def _extract_quotes(self, response):
        """Extract individual quote elements from the response.
        
        This method should be overridden or customized per website structure.
        For Correios, we look for the tariff table rows.
        """
        # Look for the tariff table - this is Correios-specific HTML structure
        quotes = []
        
        # Try to find rows in the tariff table
        rows = response.xpath(
            '//table[contains(@class, " tabela-precos") or '
            '//table[contains(@id, "tabela")]/tr'
        )
        
        if rows:
            for row in rows[1:]:  # Skip header row
                cols = row.xpath(".//td//text()").getall()
                cols = [c.strip() for c in cols if c.strip()]
                
                if len(cols) >= 5:
                    # Typical Correios table columns:
                    # service, price, delivery_time, etc.
                    quote_data = {
                        "service": cols[0] if len(cols) > 0 else None,
                        "price": cols[1] if len(cols) > 1 else None,
                        "prazo_entrega": cols[2] if len(cols) > 2 else None,
                        "disponivel": cols[3] if len(cols) > 3 else None,
                        "numero_rastreio": cols[4] if len(cols) > 4 else None,
                    }
                    quotes.append(quote_data)
        
        # If no table found, try alternative parsing
        if not quotes:
            # Look for JSON data in the page
            json_match = re.search(
                r'"tarifas"\s*:\s*(\[.*?\])',
                response.text,
                re.DOTALL
            )
            if json_match:
                try:
                    tariffs = json.loads(json_match.group(1))
                    for t in tariffs:
                        quotes.append({
                            "service": t.get("nome"),
                            "price": t.get("valor"),
                            "prazo_entrega": t.get("prazo"),
                            "disponivel": t.get("disponivel"),
                        })
                except json.JSONDecodeError:
                    pass
        
        return quotes
    
    def handle_error(self, failure):
        """Handle request errors gracefully."""
        self.logger.error(
            "Error requesting Correios: %s",
            failure.value,
            exc_info=failure.value,
        )
        
        # Yield an item indicating the service is unavailable
        yield {
            "provider": "correios",
            "service": "ERROR",
            "price": None,
            "delivery_time": None,
            "currency": "BRL",
            "available": False,
            "tracking_number": None,
            "raw_html": None,
            "_error": str(failure.value),
        }