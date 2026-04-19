import json
from typing import List, Dict

def prepare_reviews_for_llm(review_batches: List[Dict]) -> List[str]:
    """
    Extracts only the review snippets and organizes them into readable strings.
    """
    flattened_texts = []
    for batch in review_batches:
        for review in batch.get("reviews", []):
            snippet = review.get("snippet", "").strip()
            if snippet:
                flattened_texts.append(f"({review.get('rating')} stars) {snippet}")
    return flattened_texts

def calculate_cluster_metrics(clusters: List[Dict], all_reviews: List[Dict]) -> List[Dict]:
    """
    Map the LLM's semantic clusters back to the raw star ratings to calculate 'avg_rating' and 'prevalence'.
    """
    return clusters

def save_raw_reviews(data: List[Dict], filename: str = "output/raw_reviews/latest_fetch.json"):
    """Saves the raw SerpApi data to disk for audit/credit protection."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Raw reviews saved to {filename}")
