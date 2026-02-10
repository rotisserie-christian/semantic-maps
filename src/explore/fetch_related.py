from typing import List, Dict
from src.validate.fetch_trends import TrendsAPIClient


def extract_related_queries(
    api_response: Dict,
    max_queries: int = 5
) -> List[str]:
    """
    Extract related query strings from API response
    
    Args:
        api_response: Raw API response from fetch_related_queries
        max_queries: Maximum number of queries to return
        
    Returns:
        List of related query strings
    """
    if "error" in api_response:
        return []
    
    queries = []
    
    # Extract from "top" related queries
    top = api_response.get("related_queries", {}).get("top", [])
    for item in top:
        if "query" in item:
            queries.append(item["query"])
    
    # Extract from rising related queries, if not already in list
    rising = api_response.get("related_queries", {}).get("rising", [])
    for item in rising:
        if "query" in item and item["query"] not in queries:
            queries.append(item["query"])
    
    return queries[:max_queries]


def fetch_related_for_queries(
    queries: List[str],
    client: TrendsAPIClient,
    max_related_per_query: int = 5
) -> Dict[str, List[str]]:
    """
    Fetch related queries for multiple queries.
    
    Args:
        queries: List of queries to fetch related queries for
        client: Initialized TrendsAPIClient
        max_related_per_query: Max related queries per query
        
    Returns:
        Dict mapping original query -> list of related queries
    """
    related_map = {}
    
    for i, query in enumerate(queries):
        print(f"  Fetching related queries for '{query}' ({i+1}/{len(queries)})...")
        
        response = client.fetch_related_queries(query)
        related = extract_related_queries(response, max_related_per_query)
        
        if related:
            related_map[query] = related
            print(f"    Found {len(related)} related queries")
        else:
            print(f"    No related queries found")
    
    return related_map
