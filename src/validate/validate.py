import json
from pathlib import Path
from typing import List, Dict, Tuple
from .fetch_trends import TrendsAPIClient
from .analyze_interest import extract_query_interest_from_batch
from .fetch_related import fetch_related_for_queries
from .consolidate_results import consolidate_validated_results
from .save_validated import save_validated_json
from .config import serpapi_config, validation_config


def load_generated_queries(json_path: Path) -> List[Tuple[str, str]]:
    """
    Args:
        json_path: Path to searchtermsN.json file
        
    Returns:
        List of (cluster, query) tuples
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    queries = []
    
    # Handle different JSON formats
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                # Format from generate_consolidated_clusters
                if "cluster" in item and "queries" in item:
                    for query in item["queries"]:
                        queries.append((item["cluster"], query))
                # Format from flattened clusters (cluster, query) tuples
                elif "cluster" in item and "query" in item:
                    queries.append((item["cluster"], item["query"]))
    
    return queries


def batch_fetch_interest(
    queries: List[str],
    client: TrendsAPIClient
) -> Dict[str, Dict]:
    """
    Args:
        queries: List of query strings
        client: Initialized TrendsAPIClient
        
    Returns:
        Dict mapping query -> interest metrics
    """
    batch_size = serpapi_config["batch_size"]
    interest_data = {}
    
    total_batches = (len(queries) + batch_size - 1) // batch_size
    
    for i in range(0, len(queries), batch_size):
        batch = queries[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"  Batch {batch_num}/{total_batches}: {len(batch)} queries...")
        
        response = client.fetch_interest_over_time(batch)
        
        # Extract metrics for each query in batch
        for idx, query in enumerate(batch):
            metrics = extract_query_interest_from_batch(response, query, idx)
            if metrics and metrics["avg_interest"] > 0:
                interest_data[query] = metrics
    
    return interest_data


def run_validation(
    input_json_path: str | Path
) -> Path:
    """
    Run the complete validation workflow
    
    Args:
        input_json_path: Path to generated searchtermsN.json
        
    Returns:
        Path to saved validatedtermsN.json file
    """
    input_path = Path(input_json_path)
    
    # Load config values
    interest_threshold = validation_config["interest_threshold"]
    related_threshold = validation_config["related_threshold"]
    max_related_per_query = validation_config["max_related_per_query"]
    
    # Initialize API client
    print("Initializing SerpAPI client...")
    try:
        client = TrendsAPIClient()
    except RuntimeError as e:
        print(f"\nError: {e}")
        print("\nTo fix this:")
        print("1. Get your API key at https://serpapi.com/manage-api-key")
        print("2. Set environment variable:")
        print("   Linux/Mac: export SERPAPI_API_KEY='your_key_here'")
        print("   Windows:   $env:SERPAPI_API_KEY = 'your_key_here'")
        raise
    
    # 1. Load generated queries
    print(f"\nLoading generated queries from {input_path}...")
    original_queries = load_generated_queries(input_path)
    unique_clusters = len(set(c for c, q in original_queries))
    print(f"  Loaded {len(original_queries)} queries from {unique_clusters} clusters")
    
    if not original_queries:
        print("\nError: No queries found in input file.")
        print("Make sure the JSON file has the correct format.")
        return None
    
    # 2. Fetch interest for all generated queries
    print(f"\nFetching interest data for generated queries...")
    query_list = [q for c, q in original_queries]
    interest_data = batch_fetch_interest(query_list, client)
    print(f"  Got interest data for {len(interest_data)}/{len(query_list)} queries")
    
    # 3. Filter to high performers
    validated_queries = [
        q for q in query_list 
        if q in interest_data and interest_data[q]["avg_interest"] >= interest_threshold
    ]
    print(f"  {len(validated_queries)} queries above threshold ({interest_threshold})")
    
    if not validated_queries:
        print(f"\nWarning: No queries meet the interest threshold of {interest_threshold}")
        print(f"Consider lowering the threshold in src/validate/config.py")
        print("\nSaving results with only generated queries...")
        
        # Save what we have
        from datetime import datetime
        timestamp = datetime.utcnow().isoformat() + "Z"
        results = []
        for cluster, query in original_queries:
            if query in interest_data:
                results.append({
                    "cluster": cluster,
                    "query": query,
                    "source": "generated",
                    "metrics": interest_data[query],
                    "related_to": None,
                    "timestamp": timestamp
                })
        
        output_path = save_validated_json(results)
        return output_path
    
    # 4. Fetch related queries for validated terms
    print(f"\nFetching related queries for validated terms (max {max_related_per_query} per query)...")
    related_queries = fetch_related_for_queries(validated_queries, client, max_related_per_query)
    
    total_related = sum(len(r) for r in related_queries.values())
    print(f"  Found {total_related} related queries from {len(related_queries)} parent queries")
    
    # 5. Fetch interest for all unique related queries
    if total_related > 0:
        print(f"\nFetching interest data for related queries...")
        all_related = list(set(q for queries in related_queries.values() for q in queries))
        related_interest = batch_fetch_interest(all_related, client)
        print(f"  Got interest data for {len(related_interest)}/{len(all_related)} related queries")
    else:
        related_interest = {}
        print("\n  No related queries to validate")
    
    # 6. Consolidate results
    print(f"\nConsolidating results...")
    validated_results = consolidate_validated_results(
        original_queries,
        interest_data,
        related_queries,
        related_interest,
        interest_threshold,
        related_threshold
    )
    
    generated_count = sum(1 for v in validated_results if v["source"] == "generated")
    related_count = sum(1 for v in validated_results if v["source"] == "related")
    
    print(f"  Final validated set: {len(validated_results)} queries")
    print(f"    - {generated_count} from generated queries")
    print(f"    - {related_count} from related queries")
    
    # 7. Save to JSON
    output_path = save_validated_json(validated_results)
    
    return output_path