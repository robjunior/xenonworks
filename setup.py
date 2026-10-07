from setuptools import setup, find_packages

setup(
    name="freight_monitor",
    version="0.1.0",
    packages=find_packages(),
    entry_points={"scrapy": ["settings = freight_monitor.settings"]},
)
