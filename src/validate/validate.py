import json
from pathlib import Path
from typing import List, Dict, Tuple
from .fetch_trends import TrendsAPIClient
from .analyze_interest import extract_query_interest_from_batch
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
    Run simplified validation: fetch interest for all queries and return them.
    
    Args:
        input_json_path: Path to generated searchtermsN.json
        
    Returns:
        Path to saved validatedtermsN.json file
    """
    input_path = Path(input_json_path)
    
    # Initialize API client
    print("Initializing SerpAPI client...")
    try:
        client = TrendsAPIClient()
    except RuntimeError as e:
        print(f"\nError: {e}")
        raise
    
    # 1. Load generated queries
    print(f"\nLoading generated queries from {input_path}...")
    original_queries = load_generated_queries(input_path)
    if not original_queries:
        print("\nError: No queries found in input file.")
        return None
    
    # 2. Fetch interest for all generated queries
    print(f"\nFetching interest data for {len(original_queries)} queries...")
    query_list = [q for c, q in original_queries]
    interest_data = batch_fetch_interest(query_list, client)
    
    # 3. Filter and format results (omitting queries with 0 data)
    from datetime import datetime
    timestamp = datetime.utcnow().isoformat() + "Z"
    results = []
    omitted_count = 0
    
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
        else:
            omitted_count += 1
    
    # Sort by avg_interest descending
    results.sort(key=lambda x: x["metrics"]["avg_interest"], reverse=True)
    
    # 4. Save to JSON
    output_path = save_validated_json(results)
    
    print(f"\nValidation complete! Saved results for {len(results)} queries (omitted {omitted_count} with 0 data) to {output_path}")
    return output_path
