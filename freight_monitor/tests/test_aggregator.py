"""
Tests for freight_monitor aggregator.

Validates the ShippingAggregator class:
- Aggregation from multiple providers
- Cheapest and fastest option identification
- Price and delivery time ordering
- Error handling per provider
"""

import json
from freight_monitor.aggregator import ShippingAggregator
from freight_monitor.contracts import ShippingQuote


class TestAggregator:
    """Test suite for ShippingAggregator."""

    def test_aggregation_basic(self):
        """Test basic aggregation from two providers."""
        # Mock shipping spider output (as Scrapy Items with list fields)
        shipping_data = [
            {"provider": ["correios"], "service": ["SEDEX"], "price": [31.0],
             "delivery_time": [6], "currency": ["BRL"],
             "available": [True], "tracking_number": ["SG773431"]},
            {"provider": ["correios"], "service": ["PAC"], "price": [26.0],
             "delivery_time": [6], "currency": ["BRL"],
             "available": [True], "tracking_number": ["AS773431"]},
        ]

        # Mock Jadlog spider output
        jadlog_data = [
            {"provider": ["jadlog"], "service": ["Jadlog Express"], "price": [33.0],
             "delivery_time": [3], "currency": ["BRL"],
             "available": [True], "tracking_number": ["J773431"]},
            {"provider": ["jadlog"], "service": ["Jadlog Priority"], "price": [29.0],
             "delivery_time": [3], "currency": ["BRL"],
             "available": [True], "tracking_number": ["P773431"]},
        ]

        agg = ShippingAggregator(providers=["correios", "jadlog"])
        agg.collect_all(shipping_data)
        agg.collect_all(jadlog_data)

        result = agg.aggregate()

        # Verify structure
        assert "cheapest_option" in result
        assert "fastest_option" in result
        assert "all_options" in result
        assert "by_price" in result
        assert "by_delivery_time" in result
        assert "by_provider" in result
        assert "errors" in result
        assert "summary" in result

        # Verify cheapest and fastest are different providers
        assert result["cheapest_option"]["provider"] != \
            result["fastest_option"]["provider"]

        # Verify all options count
        assert len(result["all_options"]) == 4  # 2 from shipping + 2 from jadlog

        # Verify per-provider counts
        provider_counts = {k: v["total"] for k, v in result["by_provider"].items()}
        assert provider_counts["correios"] == 2
        assert provider_counts["jadlog"] == 2

    def test_cheapest_option(self):
        """Test that cheapest option is correctly identified."""
        # Mock shipping spider output (as Scrapy Items with list fields)
        shipping_data = [
            {"provider": ["correios"], "service": ["SEDEX"], "price": [31.0],
             "delivery_time": [6], "currency": ["BRL"],
             "available": [True], "tracking_number": ["SG773431"]},
        ]

        # Mock Jadlog spider output
        jadlog_data = [
            {"provider": ["jadlog"], "service": ["Jadlog Express"], "price": [33.0],
             "delivery_time": [3], "currency": ["BRL"],
             "available": [True], "tracking_number": ["J773431"]},
            {"provider": ["jadlog"], "service": ["Jadlog Priority"], "price": [29.0],
             "delivery_time": [3], "currency": ["BRL"],
             "available": [True], "tracking_number": ["P773431"]},
        ]

        agg = ShippingAggregator(providers=["correios", "jadlog"])
        agg.collect_all(shipping_data)
        agg.collect_all(jadlog_data)

        result = agg.aggregate()

        # Cheapest should be Jadlog Priority at R$29.00 (lowest price overall)
        assert result["cheapest_option"]["service"] == "Jadlog Priority"
        assert result["cheapest_option"]["price"] == 29.0

        # Fastest should be Jadlog Express at 3 days
        assert result["fastest_option"]["service"] == "Jadlog Express"
        assert result["fastest_option"]["delivery_time"] == 3

    def test_ordering_by_price(self):
        """Test that options are ordered by price ascending."""
        data = [
            {"provider": ["jadlog"], "service": ["Jadlog Express"], "price": [33.0],
             "delivery_time": [3], "currency": ["BRL"],
             "available": [True], "tracking_number": ["J773431"]},
            {"provider": ["correios"], "service": ["PAC"], "price": [26.0],
             "delivery_time": [6], "currency": ["BRL"],
             "available": [True], "tracking_number": ["AS773431"]},
            {"provider": ["correios"], "service": ["SEDEX"], "price": [31.0],
             "delivery_time": [6], "currency": ["BRL"],
             "available": [True], "tracking_number": ["SG773431"]},
        ]

        agg = ShippingAggregator(providers=["correios", "jadlog"])
        agg.collect_all(data)

        result = agg.aggregate()

        por_preco = result["by_price"]
        # Verify ascending order
        for i in range(len(por_preco) - 1):
            assert por_preco[i]["price"] <= por_preco[i + 1]["price"]

    def test_ordering_by_delivery_time(self):
        """Test that options are ordered by delivery time ascending."""
        data = [
            {"provider": ["correios"], "service": ["PAC"], "price": [26.0],
             "delivery_time": [6], "currency": ["BRL"],
             "available": [True], "tracking_number": ["AS773431"]},
            {"provider": ["jadlog"], "service": ["Jadlog Express"], "price": [33.0],
             "delivery_time": [3], "currency": ["BRL"],
             "available": [True], "tracking_number": ["J773431"]},
            {"provider": ["correios"], "service": ["SEDEX"], "price": [31.0],
             "delivery_time": [6], "currency": ["BRL"],
             "available": [True], "tracking_number": ["SG773431"]},
        ]

        agg = ShippingAggregator(providers=["correios", "jadlog"])
        agg.collect_all(data)

        result = agg.aggregate()

        por_prazo = result["by_delivery_time"]
        # Verify ascending order
        for i in range(len(por_prazo) - 1):
            assert por_prazo[i]["delivery_time"] <= por_prazo[i + 1]["delivery_time"]

    def test_summary_content(self):
        """Test that summary contains expected content."""
        data = [
            {"provider": ["correios"], "service": ["PAC"], "price": [26.0],
             "delivery_time": [6], "currency": ["BRL"],
             "available": [True], "tracking_number": ["AS773431"]},
            {"provider": ["jadlog"], "service": ["Jadlog Express"], "price": [33.0],
             "delivery_time": [3], "currency": ["BRL"],
             "available": [True], "tracking_number": ["J773431"]},
        ]

        agg = ShippingAggregator(providers=["correios", "jadlog"])
        agg.collect_all(data)

        result = agg.aggregate()

        summary = result["summary"]
        # Should mention cheapest and fastest
        assert "Cheapest:" in summary
        assert "Fastest:" in summary
        # Should mention providers
        assert "correios" in summary
        assert "jadlog" in summary

    def test_empty_aggregation(self):
        """Test aggregation with no quotes."""
        agg = ShippingAggregator(providers=["correios", "jadlog"])
        result = agg.aggregate()

        # Should return empty structure
        assert result["cheapest_option"] is None
        assert result["fastest_option"] is None
        assert result["all_options"] == []
        assert result["by_price"] == []
        assert result["by_delivery_time"] == []
        assert result["by_provider"] == {}
        assert "No freight available" in result["summary"]
