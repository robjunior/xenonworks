# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


# Pipeline for normalizing and validating shipping quote items
class FreightQuotePipeline:
    """Pipeline that normalizes and validates ShippingQuoteItem fields."""

    def process_item(self, item, spider):
        """Process and normalize the ShippingQuoteItem.

        Ensures:
        - Price is a float or None
        - Delivery time is an int or None
        - Available is a boolean
        - Currency is set correctly
        """
        adapter = ItemAdapter(item)

        # Normalize price
        if "price" in adapter:
            price = adapter.get("price")
            if price is not None:
                try:
                    adapter["price"] = float(price)
                except (ValueError, TypeError):
                    adapter["price"] = None

        # Normalize delivery_time
        if "delivery_time" in adapter:
            dt = adapter.get("delivery_time")
            if dt is not None:
                try:
                    adapter["delivery_time"] = int(dt)
                except (ValueError, TypeError):
                    adapter["delivery_time"] = None

        # Ensure available is boolean
        if "available" in adapter:
            adapter["available"] = bool(adapter.get("available", False))

        # Ensure currency
        if "currency" not in adapter:
            adapter["currency"] = "BRL"

        return item