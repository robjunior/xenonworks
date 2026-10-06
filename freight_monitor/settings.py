# Scrapy settings for freight_monitor project
#
# For simplicity, this file only contains the most important or commonly
# used settings. For more settings, see the documentation:
# https://docs.scrapy.org/en/latest/topics/settings.html
#
# The settings become part of the Scrapy object. You can access them
# via crawler.settings.getstring()s, crawler.settings.getint(), etc.
#
# Feel free to override settings on a per-spider basis during
# instantiation.

import os

BOT_NAME = "freight_monitor"

SPIDER_MODULES = ["freight_monitor.spiders"]

NEWSPIDER_MODULE = "freight_monitor.spiders"

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "freight_monitor (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
#CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 1.5

# Enable random download delay between DOWNLOAD_DELAY and DOWNLOAD_DELAY + 0.5
RANDOMIZE_DOWNLOAD_DELAY = True

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "freight_monitor.middlewares.FreightSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "freight_monitor.middlewares.FreightDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "freight_monitor.pipelines.validate.ValidationPipeline": 100,
#    "freight_monitor.pipelines.normalize.NormalizePipeline": 200,
#    "freight_monitor.pipelines.dedup.DedupPipeline": 300,
#    "freight_monitor.pipelines.storage.StoragePipeline": 400,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay value (default: 5)
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

# --- Environment -----------------------------------------------------------
# Scrapy Cloud defines SHUB_JOBKEY within jobs; it doesn't exist locally.
RUNNING_ON_CLOUD = "SHUB_JOBKEY" in os.environ

# --- Basic Crawler Configuration ------------------------------------------
# User agent string used for all requests
USER_AGENT = "freight-monitor/0.1 (project for study; contact: your-email@exemplo.com)"

# Configure maximum concurrent requests performed by Scrapy (default: 8)
CONCURRENT_REQUESTS = 8

# Configure maximum concurrent requests performed by Scrapy per domain (default: 8)
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# Configure a download delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 1.5

# Enable random download delay between DOWNLOAD_DELAY and DOWNLOAD_DELAY + 0.5
RANDOMIZE_DOWNLOAD_DELAY = True

# --- AutoThrottle Configuration -------------------------------------------
# Enable and use the AutoThrottle extension (disabled by default)
AUTOTHROTTLE_ENABLED = True

# The initial download delay value (default: 5)
AUTOTHROTTLE_START_DELAY = 2

# The maximum download delay to be set by the AutoThrottle extension (default: 60)
AUTOTHROTTLE_MAX_DELAY = 30

# The average number of concurrent requests AutoThrottle will target (default: 1.0)
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# --- Retry Configuration --------------------------------------------------
# Enable retry mechanism (disabled by default)
RETRY_ENABLED = True

# The maximum number of retry attempts (default: 0)
RETRY_TIMES = 3

# HTTP status codes for which the retry mechanism will be applied (default: [])
RETRY_HTTP_CODES = [429, 500, 502, 503, 504, 522, 524, 408]

# --- HTTP Cache Configuration ---------------------------------------------
# Enable HTTP cache (disabled by default)
HTTPCACHE_ENABLED = not RUNNING_ON_CLOUD

# The amount of seconds HTTP cache should consider an response stale (default: 0)
HTTPCACHE_EXPIRATION_SECS = 6 * 3600

# --- Secrets / External Configuration ------------------------------------
# In Scrapy Cloud, define DATABASE_URL in Settings (project or spider) in the
# dashboard; it overwrites this value. Never commit credentials.
# In pipelines, read with crawler.settings.get("DATABASE_URL").
DATABASE_URL = os.getenv("DATABASE_URL", "")

# --- Downloader Middlewares -----------------------------------------------
# Enable and configure downloader middlewares
# See: https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # "freight_monitor.middlewares.region.RegionMiddleware": 540,
    # "freight_monitor.middlewares.age_gate.AgeGateMiddleware": 550,
    # "freight_monitor.middlewares.backoff.BackoffMiddleware": 560,
}

# --- Item Pipelines -------------------------------------------------------
# Enable and configure item pipelines. See documentation for more details:
# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# The pipelines down here are commented out by default; enable them as needed:
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # "freight_monitor.pipelines.validate.ValidationPipeline": 100,
    # "freight_monitor.pipelines.normalize.NormalizePipeline": 200,
    # "freight_monitor.pipelines.dedup.DedupPipeline": 300,
    # "freight_monitor.pipelines.storage.StoragePipeline": 400,
}

# --- Spidermon ------------------------------------------------------------
# Spidermon configuration for Scrapy monitoring (optional)
# SPIDERMON_ENABLED = True  # Disable if spidermon not installed
#
# Extensions (commented out if spidermon not available)
# EXTENSIONS = {
#     "spidermon.contrib.scrapy.extensions.Spidermon": 500,
# }
#
# Spidermon spider close monitors (commented out if spidermon not available)
# SPIDERMON_SPIDER_CLOSE_MONITORS = (
#     "freight_monitor.monitors.SpiderCloseMonitorSuite",
# )

# --- Spidermon Limits -----------------------------------------------------
# Limits used by native monitors (adjust after seeing real jobs)
SPIDERMON_MIN_ITEMS = 100
SPIDERMON_MAX_ERRORS = 0
SPIDERMON_MAX_RETRIES = 50

# Unwanted HTTP codes monitored by Spidermon
SPIDERMON_UNWANTED_HTTP_CODES = {
    code: 10 for code in [400, 403, 404, 429, 500, 502, 503]
}

# --- Field Coverage -------------------------------------------------------
# Minimum fraction of items with the field filled
SPIDERMON_ADD_FIELD_COVERAGE = True

# Spidermon field coverage rules
SPIDERMON_FIELD_COVERAGE_RULES = {
    "dict/appid": 1.0,
    "dict/name": 1.0,
    "dict/currency": 0.95,
    "dict/price_final_cents": 0.85,
}

# --- Invalid Items Tolerance ---------------------------------------------
# Maximum tolerated ratio of invalid items (counted by validation pipeline)

# --- Warnings -------------------------------------------------------------
# Configure email/Slack warnings via settings dashboard when desired
FEED_EXPORT_ENCODING = "utf-8"

# Log level
LOG_LEVEL = "INFO"