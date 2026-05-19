import os
import json
from .fetch_places import fetch_top_places
from .fetch_reviews import fetch_reviews_for_places
from .processor import prepare_reviews_for_llm, save_raw_reviews
from src.utils.logger import get_logger

logger = get_logger(__name__)

def run_reviews(query: str, business_type: str = None, load_raw_path: str = None):
    """
    Orchestrates the full reviews pipeline.
    """
    if load_raw_path:
        logger.info(f"Loading raw reviews from: {load_raw_path}")
        try:
            with open(load_raw_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load raw data: {e}")
            return
    else:
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
            # 2 pages of Highest + 2 pages of Lowest per business
            raw_data = fetch_reviews_for_places(places, max_pages_per_side=2)
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
        
        # 3. LLM Semantic Clustering
        from src.llm.assemble_prompts import build_review_prompt
        from src.llm.query_llm import query_llm
        from src.llm.save_output import save_reviews_to_json
        from .processor import calculate_cluster_metrics
        
        prompt = build_review_prompt(review_texts)
        
        logger.info("Executing semantic clustering via LLM...")
        llm_response = query_llm(prompt_override=prompt, return_raw=True)
        
        # Clean potential markdown from response
        if "```json" in llm_response:
            llm_response = llm_response.split("```json")[1].split("```")[0].strip()
        elif "```" in llm_response:
            llm_response = llm_response.split("```")[1].split("```")[0].strip()
            
        clusters = json.loads(llm_response)
        
        # 4. Calculate Final Metrics (Prevalence & Impact)
        final_clusters = calculate_cluster_metrics(clusters, raw_data)
        
        # 5. Save Final Output
        output_path = save_reviews_to_json(final_clusters)
        
        logger.info("-" * 40)
        logger.info("REVIEWS ANALYSIS COMPLETE")
        logger.info(f"Final output: {output_path}")
        logger.info("-" * 40)
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return
