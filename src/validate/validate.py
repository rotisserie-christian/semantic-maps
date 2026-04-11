import json
from pathlib import Path
from typing import List, Dict, Tuple
from .fetch_trends import TrendsAPIClient
from .analyze_interest import extract_query_interest_from_batch
from .save_validated import save_validated_json
from .config import serpapi_config, validation_config
from ..utils.calculations import get_scaling_multiplier, rebase_metrics


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
    client: TrendsAPIClient,
    anchor: str = None
) -> Dict[str, Dict]:
    """
    Args:
        queries: List of query strings
        client: Initialized TrendsAPIClient
        anchor: Optional anchor term to include in every batch for consistent comparison
        
    Returns:
        Dict mapping query -> interest metrics
    """
    max_batch_size = serpapi_config["batch_size"]
    
    # If anchor is provided, we need to reserve one slot for it
    if anchor:
        effective_batch_size = max_batch_size - 1
    else:
        effective_batch_size = max_batch_size
        
    interest_data = {}
    reference_anchor_val = None
    
    total_batches = (len(queries) + effective_batch_size - 1) // effective_batch_size
    
    for i in range(0, len(queries), effective_batch_size):
        batch = queries[i:i + effective_batch_size]
        batch_num = (i // effective_batch_size) + 1
        
        print(f"  Batch {batch_num}/{total_batches}: {len(batch)} queries{' + anchor' if anchor else ''}...")
        
        # Prepare request batch
        request_batch = list(batch)
        if anchor:
            request_batch.append(anchor)
        
        response = client.fetch_interest_over_time(request_batch)
        
        # Determine scaling factor if anchor is used
        multiplier = 1.0
        if anchor:
            # Anchor is always the last element in request_batch
            anchor_idx = len(request_batch) - 1
            anchor_metrics = extract_query_interest_from_batch(response, anchor, anchor_idx)
            
            if anchor_metrics:
                # Use max_interest as the reference point for scaling across batches
                current_anchor_val = anchor_metrics["max_interest"]
                
                if reference_anchor_val is None:
                    # Capture the first batch's anchor max as the global reference
                    reference_anchor_val = current_anchor_val
                    print(f"    [Scaling] Reference Anchor Max set to: {reference_anchor_val}")
                
                multiplier = get_scaling_multiplier(current_anchor_val, reference_anchor_val)
                if multiplier != 1.0:
                    print(f"    [Scaling] Batch multiplier: {multiplier:.4f}")
            else:
                print(f"    [Warning] No metrics found for anchor '{anchor}' in this batch.")

        # Extract metrics for each query in batch
        for idx, query in enumerate(batch):
            metrics = extract_query_interest_from_batch(response, query, idx)
            if metrics and metrics["avg_interest"] > 0:
                # Apply normalization if multiplier is active
                if multiplier != 1.0:
                    metrics = rebase_metrics(metrics, multiplier)
                interest_data[query] = metrics
    
    return interest_data


def validate_queries(
    original_queries: List[Tuple[str, str]],
    client: TrendsAPIClient = None,
    anchor: str = None
) -> List[Dict]:
    """
    Validates a list of (cluster, query) tuples.
    
    Args:
        original_queries: List of (cluster, query) tuples
        client: Optional TrendsAPIClient instance
        anchor: Optional anchor term for comparison
        
    Returns:
        List of validated query dicts
    """
    if not client:
        print("Initializing SerpAPI client...")
        try:
            client = TrendsAPIClient()
        except RuntimeError as e:
            print(f"\nError: {e}")
            raise

    # Fetch interest for all queries
    print(f"\nFetching interest data for {len(original_queries)} queries...")
    query_list = [q for c, q in original_queries]
    interest_data = batch_fetch_interest(query_list, client, anchor=anchor)
    
    # Omit queries with 0 data
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
    
    if omitted_count > 0:
        print(f"Omitted {omitted_count} queries with 0 data.")
        
    return results


def run_validation(
    input_json_path: str | Path,
    anchor: str = None
) -> Path:
    """
    Run simplified validation: fetch interest for all queries and return them.
    
    Args:
        input_json_path: Path to generated searchtermsN.json
        anchor: Optional anchor term for comparison
        
    Returns:
        Path to saved validatedtermsN.json file
    """
    input_path = Path(input_json_path)
    
    # Load generated queries
    print(f"\nLoading generated queries from {input_path}...")
    original_queries = load_generated_queries(input_path)
    if not original_queries:
        print("\nError: No queries found in input file.")
        return None
    
    # Validate
    results = validate_queries(original_queries, anchor=anchor)
    
    # Save to JSON
    output_path = save_validated_json(results)
    
    print(f"\nValidation complete! Saved results for {len(results)} queries to {output_path}")
    return output_path
