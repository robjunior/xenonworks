"""
Freight aggregator for freight_monitor project.

Aggregates shipping quotes from multiple providers (spiders),
eliminates invalid results, orders by price, and identifies
the cheapest and fastest options.

Conforms to contract: freight_monitor.contracts.ShippingQuote
"""

from typing import List, Dict, Any


class ShippingAggregator:
    """Aggregates shipping quotes from multiple providers."""

    def __init__(self, providers: List[str] = None):
        """Initialize the aggregator.

        Args:
            providers: List of provider names to include.
                      Defaults to ["correios", "jadlog"]
        """
        self.results: Dict[str, List] = {}
        self.errors: Dict[str, List] = {}

    def add_provider_results(self, provider: str, quotes: List):
        """Add results from a specific provider."""
        if provider not in self.results:
            self.results[provider] = []
        self.results[provider].extend(quotes)

    def collect_all(self, all_quotes: List[Dict[str, Any]]):
        """Collect all quotes from multiple sources.

        Accepts both Scrapy Item format (with list-valued fields) and
        plain dict format. Normalizes provider field to string.
        """
        for quote in all_quotes:
            # Handle Scrapy Item format where fields may be lists
            if isinstance(quote, dict):
                # Extract provider - handle both string and list format
                provider_val = quote.get("provider", quote.get("provider", ["unknown"])[0] if isinstance(quote.get("provider"), list) else quote.get("provider", "unknown"))
                if isinstance(provider_val, list):
                    provider = provider_val[0] if provider_val else "unknown"
                else:
                    provider = str(provider_val)
            else:
                provider = str(quote) if quote else "unknown"

            if provider not in self.results:
                self.results[provider] = []
            self.results[provider].append(quote)

    def aggregate(self) -> Dict[str, Any]:
        """Aggregate and rank all collected quotes."""
        all_quotes = []
        self.errors = {}

        for provider, quotes in self.results.items():
            provider_quotes = []
            provider_errors = []

            for quote in quotes:
                # Normalize to dict if needed
                if isinstance(quote, dict):
                    # Check if Scrapy Item format (fields are lists)
                    if any(isinstance(quote.get(k), list) for k in
                           ['provider', 'service', 'price', 'delivery_time']
                           if k in quote):
                        quote_dict = {}
                        for k in ['provider', 'service', 'price', 'delivery_time',
                                  'currency', 'available', 'tracking_number']:
                            if k in quote and quote[k]:
                                quote_dict[k] = quote[k][0] \
                                    if isinstance(quote[k], list) else quote[k]
                            else:
                                quote_dict[k] = None
                    else:
                        quote_dict = dict(quote) if isinstance(quote, dict) else {}
                elif hasattr(quote, '__dict__'):
                    quote_dict = {
                        'provider': quote.provider,
                        'service': quote.service,
                        'price': quote.price,
                        'delivery_time': quote.delivery_time,
                        'currency': quote.currency,
                        'available': quote.available,
                        'tracking_number': quote.tracking_number,
                    }
                else:
                    quote_dict = dict(quote) if isinstance(quote, dict) else {}

                # Validate provider
                if not quote_dict.get("provider"):
                    provider_errors.append(
                        f"Quote missing provider: {quote}")
                    continue

                # Validate price
                if quote_dict.get("price") is not None:
                    try:
                        quote_dict["price"] = float(quote_dict["price"])
                    except (ValueError, TypeError):
                        provider_errors.append(
                            f"Invalid price for {provider}")
                        continue

                # Validate delivery_time
                if quote_dict.get("delivery_time") is not None:
                    try:
                        quote_dict["delivery_time"] = int(
                            quote_dict["delivery_time"])
                    except (ValueError, TypeError):
                        provider_errors.append(
                            f"Invalid delivery_time for {provider}")
                        continue

                all_quotes.append(quote_dict)
                provider_quotes.append(quote_dict)

            if provider_errors:
                self.errors[provider] = provider_errors

            self.results[provider] = provider_quotes

        if not all_quotes:
            return self._empty_result()

        # Order by price (ascending)
        por_preco = sorted(
            all_quotes,
            key=lambda x: x.get("price", float("inf")) or float("inf"))

        # Order by delivery time (ascending)
        por_prazo = sorted(
            all_quotes,
            key=lambda x: x.get("delivery_time", float("inf")) or float("inf"))

        # Filter only available quotes
        available_quotes = [q for q in all_quotes
                           if q.get("available", False)]

        # Cheapest (lowest price among available)
        mais_barato = min(
            available_quotes,
            key=lambda x: x.get("price", float("inf")) or float("inf")
        ) if available_quotes else None

        # Fastest (shortest delivery among available)
        mais_rapido = min(
            available_quotes,
            key=lambda x: x.get("delivery_time", float("inf")) or float("inf")
        ) if available_quotes else None

        # Per-provider summaries
        por_provedor = {}
        for provider, quotes in self.results.items():
            provider_available = [q for q in quotes
                                  if q.get("available", False)]
            por_provedor[provider] = {
                "total": len(quotes),
                "available": len(provider_available),
                "quotes": provider_available,
            }

        return {
            "cheapest_option": mais_barato,
            "fastest_option": mais_rapido,
            "all_options": all_quotes,
            "by_price": por_preco,
            "by_delivery_time": por_prazo,
            "by_provider": por_provedor,
            "errors": self.errors,
            "summary": self._generate_summary(
                mais_barato, mais_rapido, por_preco, por_prazo, por_provedor),
        }

    def _empty_result(self) -> Dict[str, Any]:
        """Return result structure when no quotes available."""
        return {
            "cheapest_option": None,
            "fastest_option": None,
            "all_options": [],
            "by_price": [],
            "by_delivery_time": [],
            "by_provider": {},
            "errors": {"global": "No quotes available"},
            "summary": "No freight available for the provided CEPs and dimensions.",
        }

    def _generate_summary(
        self,
        cheapest_option,
        fastest_option,
        by_price,
        by_delivery_time,
        by_provider,
    ) -> str:
        """Generate human-readable summary string."""
        lines: List[str] = []

        if cheapest_option:
            price_str = (
                f"R$ {cheapest_option['price']:.2f}"
                if cheapest_option.get('price') else "Unavailable")
            lines.append(
                f"Cheapest: {cheapest_option['provider']} - "
                f"{cheapest_option['service']} - "
                f"{price_str} - "
                f"{cheapest_option['delivery_time']} days")
        else:
            lines.append("Cheapest: None available")

        if fastest_option:
            price_str = (
                f"R$ {fastest_option['price']:.2f}"
                if fastest_option.get('price') else "Unavailable")
            lines.append(
                f"Fastest: {fastest_option['provider']} - "
                f"{fastest_option['service']} - "
                f"{price_str} - "
                f"{fastest_option['delivery_time']} days")
        else:
            lines.append("Fastest: None available")

        lines.append("")
        lines.append("By price (ascending):")
        for q in by_price[:5]:  # Top 5
            price_val = q.get("price")
            price_str = f"R$ {price_val:.2f}" if price_val is not None else "Unavailable"
            lines.append(
                f"  - {q['provider']} - {q['service']} - "
                f"{price_str} - {q.get('delivery_time', 'N/A')} days")

        lines.append("")
        lines.append("By delivery time (ascending):")
        for q in by_delivery_time[:5]:  # Top 5
            time_str = f"{q.get('delivery_time', 'N/A')} days"
            price_val = q.get("price")
            price_str = f"R$ {price_val:.2f}" if price_val is not None else "Unavailable"
            lines.append(
                f"  - {q['provider']} - {q['service']} - "
                f"{price_str} - {time_str}")

        lines.append("")
        lines.append("By provider:")
        for provider, data in by_provider.items():
            available_str = (
                f"({data['available']} available)"
                if data['available'] > 0 else "(not available)")
            lines.append(
                f"  - {provider}: {data['total']} total {available_str}")

        return "\n".join(lines)