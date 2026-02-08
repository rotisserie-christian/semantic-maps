import os
import time
import requests
from typing import List, Dict, Optional
from .config import serpapi_config


class TrendsAPIClient:
    """Get Google Trends data with SerpAPI"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Args: api_key: SerpAPI key. If not provided, reads from environment variable"""
        env_var = serpapi_config["env"]
        self.api_key = api_key or os.getenv(env_var)
        
        if not self.api_key:
            raise RuntimeError(
                f"{env_var} environment variable is missing. "
            )
        
        self.base_url = serpapi_config["base_url"]
        self.default_params = serpapi_config["default_params"].copy()
        self.requests_per_second = serpapi_config["requests_per_second"]
        self.last_request_time = 0
    
    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 1.0 / self.requests_per_second
        
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        
        self.last_request_time = time.time()
    
    def fetch_interest_over_time(
        self, 
        queries: List[str],
        **kwargs
    ) -> Dict:
        """
        Args:
            queries: List of search queries (max 5 for TIMESERIES)
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Raw API response as dict
        """
        if len(queries) > 5:
            raise ValueError("Maximum 5 queries allowed for TIMESERIES data_type")
        
        self._rate_limit()
        
        params = self.default_params.copy()
        params.update({
            "q": ",".join(queries),
            "data_type": "TIMESERIES",
            "api_key": self.api_key,
        })
        params.update(kwargs)
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching interest over time: {e}")
            return {"error": str(e)}
    
    def fetch_related_queries(
        self,
        query: str,
        **kwargs
    ) -> Dict:
        """
        Fetch related queries for a single query.
        
        Args:
            query: Single search query
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Raw API response as dict
        """
        self._rate_limit()
        
        params = self.default_params.copy()
        params.update({
            "q": query,
            "data_type": "RELATED_QUERIES",
            "api_key": self.api_key,
        })
        params.update(kwargs)
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching related queries for '{query}': {e}")
            return {"error": str(e)}
    
    def fetch_interest_by_region(
        self,
        query: str,
        **kwargs
    ) -> Dict:
        """
        Fetch interest by region for a single query
        
        Args:
            query: Single search query
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Raw API response as dict
        """
        self._rate_limit()
        
        params = self.default_params.copy()
        params.update({
            "q": query,
            "data_type": "GEO_MAP_0",
            "api_key": self.api_key,
        })
        params.update(kwargs)
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching interest by region for '{query}': {e}")
            return {"error": str(e)}