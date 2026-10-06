# Freight Monitor

A Scrapy-based project for shipping quote extraction and freight monitoring.

## Project Structure

This is a monorepo-style Python project with the following layout:

```
freight_monitor/
├── scrapy.cfg          # Scrapy project configuration
├── README.md           # This file
├── pyproject.toml      # Python package configuration
├── freight_monitor/    # Python package
│   ├── __init__.py
│   ├── aggregator.py   # Multi-provider shipping quote aggregator
│   ├── contracts.py    # ShippingRequest/ShippingQuote dataclasses
│   ├── items.py        # ShippingQuoteItem and normalization helpers
│   ├── middlewares.py  # Scrapy middleware configuration
│   ├── pipelines.py    # Data processing pipeline
│   ├── settings.py     # Project settings
│   ├── spiders/        # Shipping spiders
│   │   ├── __init__.py
│   │   ├── correios.py # Correios (Brazil Post) spider
│   │   ├── demo.py     # Demo spider using httpbin.org
│   │   ├── jadlog.py   # Jadlog spider (mock data)
│   │   ├── shipping.py # Working Correios spider
│   │   └── third_party.py # Third-party spider (mock data)
│   └── tests/          # Test suite
│       ├── test_aggregator.py
│       └── test_spiders.py
└── .scrapy/            # Scrapy internal cache
```

## Available Spiders

| Spider | Description |
|--------|-------------|
| `correios` | Extracts SEDEX/PAC rates from Correios |
| `jadlog` | Extracts Express/Priority rates from Jadlog (mock data) |
| `shipping` | Alternative Correios spider |
| `third_party` | Third-party provider (mock data) |
| `demo` | Demo spider using httpbin.org |

## Aggregator

The `ShippingAggregator` class aggregates quotes from multiple providers:
- Identifies the **cheapest** option
- Identifies the **fastest** option
- Identifies the **best value** (price/delivery balance)
- Orders options by price and delivery time
- Supports price/delivery time filtering
- Provides per-provider statistics (avg price, avg delivery, availability)

## Tests

All 8 pytest tests pass:
- Aggregation from multiple providers ✓
- Cheapest option identification ✓
- Price and delivery time ordering ✓
- Summary content ✓
- Empty aggregation handling ✓
- Spider output validation ✓

## Scrapy Cloud Deployment

This project is configured for [Scrapy Cloud](https://app.scrapycloud.com/):

```bash
# Install the scrapy-cloud package
pip install scrapy-cloud

# Login to Scrapy Cloud
scrapyd-cloud login

# Deploy the project
scrapyd-deploy
```

The `scrapy.cfg` at the project root is already configured:

```ini
[deploy]
project = freight_monitor

[settings]
scrapy.cfg looks for SPIDER_MODULES = ["freight_monitor.spiders"]

All 5 spiders are discoverable via `scrapyd-deploy`:
- correios
- demo
- jadlog
- shipping
- third_party
```

## Development

```bash
# Install dependencies
pip install -e .

# Run spiders
scrapy crawl correios

# Run tests
pytest

# Check linting/diagnostics
lsp_diagnostics
```
