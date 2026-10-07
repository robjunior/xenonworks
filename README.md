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

## Tests

All 8 pytest tests pass:
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

### 1. Get your Project ID
1. Go to https://app.scrapycloud.com/
2. Create a new project or select existing one
3. Copy the **Project ID** (a number like `123456`)

### 2. Configure the project
Edit `scrapinghub.yml` and replace `YOUR_SCRAPY_CLOUD_PROJECT_ID_HERE` with your actual Project ID:
```yaml
project: 123456  # Replace with your actual Project ID
requirements:
  file: requirements.txt
```

### 3. Deploy
```bash
# Install scrapy-cloud
pip install scrapy-cloud

# Login
scrapyd-cloud login

# Deploy
scrapyd-deploy
```

### Alternative: Deploy with project ID via command line
```bash
# Without editing scrapinghub.yml
scrapyd-deploy -p YOUR_PROJECT_ID
```

### Required files for deployment
The project includes all necessary files:
- `requirements.txt` - Dependencies (scrapy, setuptools, wheel)
- `setup.py` - Python package setup with Scrapy entry point
- `scrapinghub.yml` - Project configuration (set your Project ID)
- `scrapy.cfg` - Scrapy configuration (project = freight_monitor)

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

## Docker

```bash
# Build and run tests in container
docker compose up --build

# Or run specific commands in container
docker compose run freight-monitor pytest tests/
docker compose run freight-monitor scrapy crawl correios
```

## License

MIT License
