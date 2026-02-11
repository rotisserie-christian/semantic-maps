import json
from pathlib import Path
from typing import List, Dict
from ..validate.fetch_trends import TrendsAPIClient
from .fetch_related import fetch_related_for_queries

def load_search_terms(json_path: Path) -> List[Dict]:
    """Load queries from a searchterms JSON file"""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_search_terms(json_path: Path, data: List[Dict]):
    """Save updated search terms back to the same file"""
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def run_explore(input_json_path: str | Path) -> Path:
    """
    Fetch related queries and merge them into the original searchterms JSON file
    Updates the file in-place by adding related queries to each cluster
    
    Args:
        input_json_path: Path to searchtermsN.json file
        
    Returns:
        Path to the updated file (same as input)
    """
    input_path = Path(input_json_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    print(f"Loading search terms from {input_path}...")
    clusters = load_search_terms(input_path)
    if not clusters:
        print("No clusters found in input file.")
        return None

    # Initialize API 
    print("Initializing SerpAPI client...")
    client = TrendsAPIClient()

    # Extract all unique queries
    all_queries = []
    for cluster in clusters:
        all_queries.extend(cluster.get("queries", []))
    
    print(f"\nFetching related queries for {len(all_queries)} queries...")
    related_map = fetch_related_for_queries(all_queries, client, max_related_per_query=5)

    # map query -> cluster 
    query_to_cluster = {}
    for cluster in clusters:
        cluster_name = cluster["cluster"]
        for query in cluster.get("queries", []):
            query_to_cluster[query] = cluster_name

    # Track new queries to add to each cluster
    cluster_additions = {cluster["cluster"]: set() for cluster in clusters}
    
    # Process related queries
    total_related = 0
    for original_query, related_queries in related_map.items():
        cluster_name = query_to_cluster.get(original_query)
        if cluster_name:
            for related in related_queries:
                # Only add if not already in a cluster
                if not any(related in cluster.get("queries", []) for cluster in clusters):
                    cluster_additions[cluster_name].add(related)
                    total_related += 1

    # Add new queries to the right clusters
    for cluster in clusters:
        cluster_name = cluster["cluster"]
        new_queries = cluster_additions.get(cluster_name, set())
        if new_queries:
            cluster["queries"].extend(sorted(new_queries))
            print(f"  Added {len(new_queries)} related queries to '{cluster_name}'")

    # Save back to the same file
    save_search_terms(input_path, clusters)
    
    print(f"\nExploration complete! Added {total_related} related queries to {input_path}")
    return input_path