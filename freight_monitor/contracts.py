"""
Freight monitor project contracts.

Defines the data contracts between the system and shipping scrapers:
- ShippingRequest: Input data structure for freight requests
- ShippingQuote: Normalized output structure from all spiders
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ShippingRequest:
    """Input request for shipping quote calculation.

    All fields are required unless marked as Optional.

    Attributes:
        origin_cep: Origin ZIP code (e.g., "01001-000")
        dest_cep: Destination ZIP code (e.g., "09000-000")
        weight: Package weight in grams
        width: Width in centimeters
        height: Height in centimeters
        length: Length in centimeters (optional)
        declared_value: Declared value for the package (optional, in cents)
    """

    origin_cep: str
    dest_cep: str
    weight: float
    width: float
    height: float
    length: float = field(default=20.0)
    declared_value: Optional[float] = field(default=None, metadata={"units": "cents"})


@dataclass
class ShippingQuote:
    """Normalized shipping quote from a provider.

    All spiders must produce output conforming to this contract,
    enabling the aggregator and budget engine to work uniformly.

    Attributes:
        provider: Name of the shipping provider (e.g., "correios", "jadlog")
        service: Service name/code (e.g., "SEDEX", "PAC")
        price: Price in BRL (float), or None if unavailable
        delivery_time: Estimated delivery time in days (int), or None
        currency: Currency code (e.g., "BRL")
        available: Whether the service is available for the given route
        tracking_number: Tracking code pattern, if applicable
    """

    provider: str
    service: str
    price: Optional[float] = None
    delivery_time: Optional[int] = None
    currency: str = "BRL"
    available: bool = True
    tracking_number: Optional[str] = None


# Alias for backward compatibility and ease of use
Quote = ShippingQuote


# Example usage:
#
# from freight_monitor.contracts import ShippingRequest, ShippingQuote
#
# request = ShippingRequest(
#     origin_cep="01001-000",
#     dest_cep="09000-000",
#     weight=650.0,
#     width=20.0,
#     height=15.0,
#     length=30.0,
# )
#
# quote = ShippingQuote(
#     provider="correios",
#     service="SEDEX",
#     price=25.50,
#     delivery_time=3,
#     available=True,
#     tracking_number="SG123456",
# )
#
# # Validate that all spiders produce compatible output:
# assert isinstance(quote.price, (float, type(None)))
# assert isinstance(quote.delivery_time, (int, type(None)))
# assert quote.currency == "BRL"