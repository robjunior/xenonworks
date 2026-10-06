# Freight Monitor

A Scrapy-based project for shipping quote extraction and freight monitoring.

## Project Structure

This is a monorepo-style Python project. The Python package is at the project root:

```
freight_monitor/              # Project root
├── scrapy.cfg               # Scrapy project configuration
├── pyproject.toml           # Python package configuration
├── README.md                # This file
├── __init__.py              # Package init
├── freight_monitor/         # Python package (at root level)
│   ├── __init__.py
│   ├── aggregator.py        # Multi-provider shipping quote aggregator
│   ├── contracts.py         # ShippingRequest/ShippingQuote dataclasses
│   ├── items.py             # ShippingQuoteItem and normalization helpers
│   ├── middlewares.py       # Scrapy middleware configuration
│   ├── pipelines.py         # Data processing pipeline
│   ├── settings.py          # Project settings
│   └── spiders/             # Shipping spiders (5 total)
│       ├── __init__.py
│       ├── correios.py      # Correios (Brazil Post) spider
│       ├── demo.py          # Demo spider using httpbin.org
│       ├── jadlog.py        # Jadlog spider (mock data)
│       ├── shipping.py      # Working Correios spider
│       └── third_party.py   # Third-party spider (mock data)
├── tests/                   # Test suite
│   ├── test_aggregator.py   # 6 tests for aggregator
│   └── test_spiders.py      # 2 tests for spider output validation
└── .scrapy/                 # Scrapy internal cache
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

## Running Tests

```bash
pytest
```

All 8 tests pass:
- Aggregation from multiple providers ✓
- Cheapest option identification ✓
- Price and delivery time ordering ✓
- Summary content ✓
- Empty aggregation handling ✓
- Spider output validation ✓

## Execution

```bash
# Install dependencies
pip install -e .

# Run a spider
scrapy crawl correios

# Run all spiders via aggregator
python3 -c "
from freight_monitor.aggregator import ShippingAggregator
agg = ShippingAggregator(providers=['correios', 'jadlog'])
# Collect data and aggregate as needed
"

# Quick test
python3 -m pytest tests/ -v
```

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
```

All 5 spiders are discoverable via `scrapyd-deploy`:
- `correios`
- `demo`
- `jadlog`
- `shipping`
- `third_party`

## Development

```bash
# Install in editable mode
pip install -e .

# Run spiders
scrapy crawl correios

# Run tests
pytest

# Verify imports work
python3 -c "from freight_monitor.aggregator import ShippingAggregator; print('OK')"
```

## License

MIT License
