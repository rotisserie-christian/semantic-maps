import os
import requests
import time
from typing import List, Dict

class ReviewsAPIClient:
    """Client for extracting Google Maps Reviews via SerpApi"""
    
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise RuntimeError("SERPAPI_API_KEY environment variable is missing.")
        self.base_url = "https://serpapi.com/search"

    def fetch_all_reviews(self, data_id: str, max_pages: int = 5) -> List[Dict]:
        """
        Fetch reviews for a specific business ID, with pagination.
        
        Args:
            data_id: The unique Google Maps data ID
            max_pages: Hard cap on pages to prevent accidental credit drain
            
        Returns:
            List of review objects.
        """
        all_reviews = []
        next_token = None
        pages_fetched = 0
        
        while pages_fetched < max_pages:
            params = {
                "engine": "google_maps_reviews",
                "data_id": data_id,
                "api_key": self.api_key,
                "num": 20  # Maximize reviews per credit
            }
            if next_token:
                params["next_page_token"] = next_token
                
            try:
                response = requests.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching reviews: {e}")
                break

            reviews = data.get("reviews", [])
            all_reviews.extend(reviews)
            pages_fetched += 1
            
            print(f"  Fetched page {pages_fetched} ({len(reviews)} reviews)...")
            
            # Check for next page
            next_token = data.get("serpapi_pagination", {}).get("next_page_token")
            if not next_token or not reviews:
                break
                
        return all_reviews

def fetch_reviews_for_places(places: List[Dict], max_pages_per_place: int = 5) -> List[Dict]:
    """
    Orchestrates review collection for a list of businesses.
    """
    client = ReviewsAPIClient()
    combined_data = []
    
    for place in places:
        name = place.get("title", "Unknown")
        d_id = place.get("data_id")
        
        if not d_id:
            continue
            
        print(f"Collecting reviews for '{name}'...")
        reviews = client.fetch_all_reviews(d_id, max_pages=max_pages_per_place)
        
        combined_data.append({
            "business_info": place,
            "reviews": reviews
        })
        
    return combined_data
