import json
import os
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

def calculate_cluster_metrics(clusters: List[Dict], all_raw_data: List[Dict]) -> List[Dict]:
    """
    Map the LLM's semantic clusters back to the raw star ratings with robust matching.
    """
    # Create a list of all raw reviews for matching
    all_reviews = []
    for batch in all_raw_data:
        for r in batch.get("reviews", []):
            snippet = r.get("snippet", "").strip()
            if snippet:
                all_reviews.append(r)
    
    total_reviews = len(all_reviews)
    if total_reviews == 0:
        return clusters

    final_results = []
    for cluster in clusters:
        matches = cluster.get("matches", [])
        matched_ratings = []
        
        # For each match provided by the LLM, find which raw review it belongs to
        for m_text in matches:
            m_text_clean = str(m_text).lower().strip()
            # Handle the case where LLM includes the "(X stars)" prefix in its match
            if ") " in m_text_clean:
                m_text_clean = m_text_clean.split(") ", 1)[1]
            
            for review in all_reviews:
                snippet_clean = review.get("snippet", "").lower().strip()
                if m_text_clean in snippet_clean or snippet_clean in m_text_clean:
                    matched_ratings.append(review.get("rating", 0))
                    break # Take the first match and move to next LLM snippet
        
        if not matched_ratings:
            avg_rating = 0
            prevalence = 0
        else:
            avg_rating = sum(matched_ratings) / len(matched_ratings)
            # Prevalence is % of total reviews that mention this cluster
            prevalence = int((len(matched_ratings) / total_reviews) * 100)
            
        final_results.append({
            "feedback": cluster.get("feedback"),
            "prevalence": min(prevalence, 100),
            "impact_score": round(avg_rating, 1),
            "type": cluster.get("type")
        })
        
    return final_results

def save_raw_reviews(data: List[Dict], filename: str = "output/raw_reviews/latest_fetch.json"):
    """Saves the raw SerpApi data to disk for audit/credit protection."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Raw reviews saved to {filename}")
