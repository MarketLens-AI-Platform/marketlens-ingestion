# marketlens-ingestion

![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

Autonomous A2A (Agent-to-Agent) scraping service for Shopify and WooCommerce product catalogs. Features Playwright fallback for JS-rendered pages and Pydantic schema validation.

## Architecture

The ingestion service is designed as a decoupled component of the MarketLens AI Platform. It handles the extraction of raw product data from various e-commerce platforms and prepares it for the Enrichment and ML stages.

- **Scraping Agents**: Specialized agents for Shopify and WooCommerce.
- **Validation**: Strict Pydantic models ensure data consistency.
- **Resilience**: Integrated retry logic with `tenacity`.
- **Hybrid Approach**: Combination of direct API/JSON requests and Playwright browser automation.

## Quick Start

1. **Local Setup**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium --with-deps
   ```

2. **Run Scraper**:
   ```bash
   export PYTHONPATH=.
   python scraping/main.py
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level (INFO, DEBUG, ERROR) | `INFO` |

## Docker Usage

Build the image:
```bash
docker build -t marketlens-ingestion .
```

Run the container:
```bash
docker run marketlens-ingestion
```

---

**Part of the [MarketLens AI Platform](https://github.com/MarketLens-AI-Platform)**

Author: **Yassine Kamouss** — FST Tanger, LSI 2, 2025/2026
