"""
Freight aggregator for freight_monitor project.

Aggregates shipping quotes from multiple providers (spiders),
eliminates invalid results, orders by price/prazo, and identifies
the most barato and mais rapido options.

Conformes ao contrato: freight_monitor.contracts.ShippingQuote
"""

from typing import List, Dict, Any


class ShippingAggregator:
    """Aggregates shipping quotes from multiple providers.

    Responsibilities:
    - Execute multiple shipping providers (spiders)
    - Collect and normalize results
    - Eliminate invalid/undesired results
    - Order by price (crescente) and prazo (crescente)
    - Identify the most barato option
    - Identify the mais rapido option
    - Maintain erros individuais (nao bloqueiam o resultado)
    """

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
                                quote_dict[k] = quote[k][0] if isinstance(quote[k], list) else quote[k]
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
                    provider_errors.append(f"Quote missing provider: {quote}")
                    continue

                # Validate price
                if quote_dict.get("price") is not None:
                    try:
                        quote_dict["price"] = float(quote_dict["price"])
                    except (ValueError, TypeError):
                        provider_errors.append(f"Invalid price for {provider}")
                        continue

                # Validate delivery_time
                if quote_dict.get("delivery_time") is not None:
                    try:
                        quote_dict["delivery_time"] = int(quote_dict["delivery_time"])
                    except (ValueError, TypeError):
                        provider_errors.append(f"Invalid delivery_time for {provider}")
                        continue

                all_quotes.append(quote_dict)
                provider_quotes.append(quote_dict)

            if provider_errors:
                self.errors[provider] = provider_errors

            self.results[provider] = provider_quotes

        if not all_quotes:
            return self._empty_result()

        # Order by price (crescente)
        por_preco = sorted(
            all_quotes,
            key=lambda x: x.get("price", float("inf")) or float("inf")
        )

        # Order by delivery time (crescente)
        por_prazo = sorted(
            all_quotes,
            key=lambda x: x.get("delivery_time", float("inf")) or float("inf")
        )

        # Filter only available quotes
        available_quotes = [q for q in all_quotes if q.get("available", False)]

        # Most barato (lowest price among available)
        mais_barato = min(
            available_quotes,
            key=lambda x: x.get("price", float("inf")) or float("inf")
        ) if available_quotes else None

        # Mais rapido (shortest delivery among available)
        mais_rapido = min(
            available_quotes,
            key=lambda x: x.get("delivery_time", float("inf")) or float("inf")
        ) if available_quotes else None

        # Per-provider summaries
        por_provedor = {}
        for provider, quotes in self.results.items():
            provider_available = [q for q in quotes if q.get("available", False)]
            por_provedor[provider] = {
                "total": len(quotes),
                "available": len(provider_available),
                "quotes": provider_available,
            }

        return {
            "melhor_opcao": mais_barato,
            "mais_rapido": mais_rapido,
            "todas_as_opcoes": all_quotes,
            "por_preco": por_preco,
            "por_prazo": por_prazo,
            "por_provedor": por_provedor,
            "erros": self.errors,
            "resumo": self._generate_summary(
                mais_barato, mais_rapido, por_preco, por_prazo, por_provedor
            ),
        }

    def _empty_result(self) -> Dict[str, Any]:
        """Return result structure when no quotes available."""
        return {
            "melhor_opcao": None,
            "mais_rapido": None,
            "todas_as_opcoes": [],
            "por_preco": [],
            "por_prazo": [],
            "por_provedor": {},
            "erros": {"global": "Nenhum orcamento disponivel"},
            "resumo": "Nenhum frete disponivel para os CEPs e dimensoes informados.",
        }

    def _generate_summary(
        self,
        mais_barato,
        mais_rapido,
        por_preco,
        por_prazo,
        por_provedor,
    ) -> str:
        """Generate human-readable summary string."""
        lines = []

        if mais_barato:
            price_str = f"R$ {mais_barato['price']:.2f}" if mais_barato.get('price') else "Indisponivel"
            lines.append(
                f"Mais barato: {mais_barato['provider']} - "
                f"{mais_barato['service']} - "
                f"{price_str} - "
                f"{mais_barato['delivery_time']} dias"
            )
        else:
            lines.append("Mais barato: Nenhum disponivel")

        if mais_rapido:
            price_str = f"R$ {mais_rapido['price']:.2f}" if mais_rapido.get('price') else "Indisponivel"
            lines.append(
                f"Mais rapido: {mais_rapido['provider']} - "
                f"{mais_rapido['service']} - "
                f"{price_str} - "
                f"{mais_rapido['delivery_time']} dias"
            )
        else:
            lines.append("Mais rapido: Nenhum disponivel")

        lines.append("")
        lines.append("Por preco (crescente):")
        for q in por_preco[:5]:
            price_val = q.get("price")
            price_str = f"R$ {price_val:.2f}" if price_val is not None else "Indisponivel"
            lines.append(
                f"  - {q['provider']} - {q['service']} - "
                f"{price_str} - {q.get('delivery_time', 'N/A')} dias"
            )

        lines.append("")
        lines.append("Por prazo (crescente):")
        for q in por_prazo[:5]:
            time_str = f"{q.get('delivery_time', 'N/A')} dias"
            price_val = q.get("price")
            price_str = f"R$ {price_val:.2f}" if price_val is not None else "Indisponivel"
            lines.append(
                f"  - {q['provider']} - {q['service']} - "
                f"{price_str} - {time_str}"
            )

        lines.append("")
        lines.append("Por provedor:")
        for provider, data in por_provedor.items():
            available_str = f"({data['available']} disponiveis)" if data['available'] > 0 else "(nao disponivel)"
            lines.append(
                f"  - {provider}: {data['total']} total {available_str}"
            )

        return "\n".join(lines)