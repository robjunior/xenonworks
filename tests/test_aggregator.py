"""
Tests for freight_monitor aggregator.
"""

from freight_monitor.aggregator import ShippingAggregator


class TestAggregator:
    def test_aggregation_basic(self):
        shipping_data = [
            {"provider": ["correios"], "service": ["SEDEX"], "price": [31.0],
             "delivery_time": [6], "currency": ["BRL"],
             "available": [True], "tracking_number": ["SG773431"]},
            {"provider": ["correios"], "service": ["PAC"], "price": [26.0],
             "delivery_time": [6], "currency": ["BRL"],
             "available": [True], "tracking_number": ["AS773431"]},
        ]
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
        assert "cheapest_option" in result
        assert "fastest_option" in result
        assert "all_options" in result
        assert "by_price" in result
        assert "by_delivery_time" in result
        assert "by_provider" in result
        assert "errors" in result
        assert "summary" in result
        assert result["cheapest_option"]["provider"] != result["fastest_option"]["provider"]
        assert len(result["all_options"]) == 4
        provider_counts = {k: v["total"] for k, v in result["by_provider"].items()}
        assert provider_counts["correios"] == 2
        assert provider_counts["jadlog"] == 2

    def test_cheapest_option(self):
        shipping_data = [
            {"provider": ["correios"], "service": ["SEDEX"], "price": [31.0],
             "delivery_time": [6], "currency": ["BRL"],
             "available": [True], "tracking_number": ["SG773431"]},
        ]
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
        assert result["cheapest_option"]["service"] == "Jadlog Priority"
        assert result["cheapest_option"]["price"] == 29.0
        assert result["fastest_option"]["service"] == "Jadlog Express"
        assert result["fastest_option"]["delivery_time"] == 3

    def test_ordering_by_price(self):
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
        for i in range(len(por_preco) - 1):
            assert por_preco[i]["price"] <= por_preco[i + 1]["price"]

    def test_ordering_by_delivery_time(self):
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
        for i in range(len(por_prazo) - 1):
            assert por_prazo[i]["delivery_time"] <= por_prazo[i + 1]["delivery_time"]

    def test_summary_content(self):
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
        assert "Cheapest:" in summary
        assert "Fastest:" in summary
        assert "correios" in summary
        assert "jadlog" in summary

    def test_empty_aggregation(self):
        agg = ShippingAggregator(providers=["correios", "jadlog"])
        result = agg.aggregate()
        assert result["cheapest_option"] is None
        assert result["fastest_option"] is None
        assert result["all_options"] == []
        assert result["by_price"] == []
        assert result["by_delivery_time"] == []
        assert result["by_provider"] == {}
        assert "No freight available" in result["summary"]
