"""Entry point for testing the scraping agents."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import List

from scraping.schemas import Product
from scraping.shopify_agent import ShopifyAgent
from scraping.woocommerce_agent import WooCommerceAgent


TARGET_STORES = [
    # WooCommerce Stores
    {"platform": "woocommerce", "url": "https://themes.woocommerce.com/storefront/"},
    {"platform": "woocommerce", "url": "https://websitedemos.net/brandstore-02/"},
    {"platform": "woocommerce", "url": "https://shoprootscience.com"},
    {"platform": "woocommerce", "url": "https://www.bluestarcoffee.eu"},
    {"platform": "woocommerce", "url": "https://www.kawaiibox.com"},
    {"platform": "woocommerce", "url": "https://www.magnatiles.com"},
    {"platform": "woocommerce", "url": "https://www.chucklingcheese.co.uk"},
    {"platform": "woocommerce", "url": "https://www.sodashi.com.au"},
    {"platform": "woocommerce", "url": "https://www.printingnewyork.com"},
    {"platform": "woocommerce", "url": "https://porterandyork.com"},
    
    # Shopify Stores
    {"platform": "shopify", "url": "https://www.allbirds.com"},
    {"platform": "shopify", "url": "https://www.gymshark.com"},
    {"platform": "shopify", "url": "https://colourpop.com"},
    {"platform": "shopify", "url": "https://www.fashionnova.com"},
    {"platform": "shopify", "url": "https://skims.com"},
    {"platform": "shopify", "url": "https://kith.com"},
    {"platform": "shopify", "url": "https://bombas.com"},
    {"platform": "shopify", "url": "https://www.deathwishcoffee.com"},
    {"platform": "shopify", "url": "https://www.bulletproof.com"},
    {"platform": "shopify", "url": "https://heinztohome.co.uk"}
]


def configure_logging() -> None:
    """Configure baseline logging for local execution."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def get_output_path() -> Path:
    """Return output path for raw sample products."""
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "raw" / "sample_products.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


from confluent_kafka import Producer
import os

def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

async def run() -> None:
    """Scrape a list of target stores and publish to Kafka."""
    logger = logging.getLogger(__name__)
    
    kafka_conf = {
        'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "marketlens-kafka:9092"),
        'client.id': 'marketlens-ingestion-producer'
    }
    producer = Producer(kafka_conf)
    
    success_count = 0
    failure_count = 0

    for store in TARGET_STORES:
        platform = store["platform"]
        url = store["url"]
        
        logger.info(f"Starting scraping for {url} ({platform})")
        
        try:
            if platform == "shopify":
                agent = ShopifyAgent()
            elif platform == "woocommerce":
                agent = WooCommerceAgent()
            else:
                logger.error(f"Unsupported platform: {platform} for url: {url}")
                failure_count += 1
                continue
                
            products = await agent.scrape_store(url)
            
            for product in products:
                payload = product.model_dump_json()
                producer.produce('raw-market-data', key=product.product_id, value=payload, callback=delivery_report)
            
            producer.flush()
            
            success_count += 1
            
        except Exception as exc:
            logger.error(
                f"Failed to scrape store {url}: {exc}", 
                extra={"store": url, "error": str(exc), "platform": platform}
            )
            failure_count += 1
            continue
        finally:
            await asyncio.sleep(3)

    logger.info(
        "Final Scraping Summary",
        extra={
            "successful_stores": success_count,
            "failed_stores": failure_count
        }
    )


if __name__ == "__main__":
    configure_logging()
    asyncio.run(run())
