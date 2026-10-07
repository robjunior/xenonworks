FROM python:3.12-slim

# Install system dependencies for Scrapy
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir \
    scrapy \
    pytest \
    pytest-cov \
    && pip install --no-cache-dir \
    scrapy-cloud 2>/dev/null || echo "scrapy-cloud install attempted"

# Make pytest the entrypoint
CMD ["pytest", "tests/"]
