"""
Minimal tests for freight_monitor spiders.

Validates spider output format by checking the aggregated results,
rather than parsing raw JSON. Focuses on the aggregator which is
the core functionality.
"""

from freight_monitor.aggregator import ShippingAggregator


class TestSpidersThroughAggregator:
    """Test spider output via the aggregator."""

    def test_shipping_via_aggregator(self):
        """Test shipping spider output through aggregator."""
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

        # Verify aggregation worked
        assert len(result["all_options"]) == 4
        assert result["cheapest_option"]["provider"] == "correios"
        assert result["fastest_option"]["provider"] == "jadlog"
        assert "SEDEX" in result["summary"]
        assert "Express" in result["summary"]

    def test_jadlog_via_aggregator(self):
        """Test Jadlog spider output through aggregator."""
        # Mock Jadlog spider output (as Scrapy Items with list fields)
        jadlog_data = [
            {"provider": ["jadlog"], "service": ["Jadlog Express"], "price": [33.0],
             "delivery_time": [3], "currency": ["BRL"],
             "available": [True], "tracking_number": ["J773431"]},
            {"provider": ["jadlog"], "service": ["Jadlog Priority"], "price": [29.0],
             "delivery_time": [3], "currency": ["BRL"],
             "available": [True], "tracking_number": ["P773431"]},
        ]

        agg = ShippingAggregator(providers=["correios", "jadlog"])
        agg.collect_all(jadlog_data)

        result = agg.aggregate()

        # Verify aggregation worked with single provider
        assert len(result["all_options"]) == 2
        assert result["by_provider"]["jadlog"]["total"] == 2
        assert result["by_provider"]["jadlog"]["available"] == 2
