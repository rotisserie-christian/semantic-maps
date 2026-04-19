import os
import requests
from typing import List, Dict, Optional

class MapsAPIClient:
    """Client for interacting with Google Maps via SerpApi"""
    
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise RuntimeError("SERPAPI_API_KEY environment variable is missing.")
        self.base_url = "https://serpapi.com/search"

    def search_places(self, query: str, business_type: Optional[str] = None) -> List[Dict]:
        """
        Search for places on Google Maps and optionally filter by type.
        
        Args:
            query: The search query (e.g., "Restaurants in SoHo")
            business_type: Optional string to filter the 'type' field of results
            
        Returns:
            List of business dictionaries containing name, id, and metadata.
        """
        params = {
            "engine": "google_maps",
            "q": query,
            "api_key": self.api_key
        }
        
        print(f"Searching Google Maps for: '{query}'...")
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching places: {e}")
            return []

        local_results = data.get("local_results", [])
        if not local_results:
            print("No local results found.")
            return []

        if business_type:
            filtered = [
                res for res in local_results 
                if business_type.lower() in res.get("type", "").lower()
            ]
            print(f"Filtered {len(local_results)} results down to {len(filtered)} matching type '{business_type}'")
            return filtered
            
        return local_results

def fetch_top_places(query: str, business_type: Optional[str] = None) -> List[Dict]:
    """Helper function to initialize client and fetch places."""
    client = MapsAPIClient()
    return client.search_places(query, business_type)
