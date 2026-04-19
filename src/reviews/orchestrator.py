import os
import json
from .fetch_places import fetch_top_places
from .fetch_reviews import fetch_reviews_for_places
from .processor import prepare_reviews_for_llm, save_raw_reviews
from src.utils.logger import get_logger

logger = get_logger(__name__)

def run_reviews(query: str, business_type: str = None):
    """
    Orchestrates the full reviews pipeline.
    """
    logger.info(f"Starting Reviews Pipeline for query: '{query}'")
    if business_type:
        logger.info(f"Filtering for business type: '{business_type}'")

    # Get places
    try:
        places = fetch_top_places(query, business_type)
        if not places:
            logger.warning("No places found matching criteria.")
            return
        logger.info(f"Found {len(places)} businesses.")
    except Exception as e:
        logger.error(f"Failed to fetch places: {e}")
        return

    # Get reviews
    try:
        # Max 3 pages (60 reviews) per business
        raw_data = fetch_reviews_for_places(places, max_pages_per_place=3)
        if not raw_data:
            logger.warning("No reviews collected.")
            return
        
        save_raw_reviews(raw_data)
    except Exception as e:
        logger.error(f"Failed to fetch reviews: {e}")
        return

    try:
        review_texts = prepare_reviews_for_llm(raw_data)
        logger.info(f"Prepared {len(review_texts)} review snippets for semantic analysis.")
        
        # Connect to LLM for clustering
        logger.info("Semantic analysis phase pending LLM prompt implementation.")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return

    logger.info("Reviews pipeline step 1 & 2 complete.")
