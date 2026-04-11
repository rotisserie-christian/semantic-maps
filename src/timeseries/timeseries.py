import json
from pathlib import Path
from typing import List, Dict
from ..validate.fetch_trends import TrendsAPIClient
from ..validate.config import serpapi_config
from ..utils.calculations import get_scaling_multiplier


def load_validated_queries(json_path: Path) -> List[Dict]:
    """Load queries from a validated search terms JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_timeseries(input_json_path: str | Path, anchor: str = None) -> Path:
    """
    Fetch interest over time (timeseries) for queries in a validated JSON file.
    Saves the result to output/timeseries/timeseriesN.json.
    
    Args:
        input_json_path: Path to validated JSON
        anchor: Optional anchor term for cross-batch normalization
    """
    input_path = Path(input_json_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    print(f"Loading validated queries from {input_path}...")
    validated_data = load_validated_queries(input_path)
    if not validated_data:
        print("No queries found in input file.")
        return None

    # Initialize API client
    print("Initializing SerpAPI client...")
    client = TrendsAPIClient()

    queries = [item["query"] for item in validated_data]
    max_batch_size = serpapi_config.get("batch_size", 5)
    
    # Reserve slot for anchor
    if anchor:
        effective_batch_size = max_batch_size - 1
    else:
        effective_batch_size = max_batch_size
        
    timeseries_map = {}
    total_queries = len(queries)
    reference_anchor_val = None
    
    print(f"Fetching timeseries for {total_queries} queries in batches of {effective_batch_size}{' + anchor' if anchor else ''}...")
    
    for i in range(0, total_queries, effective_batch_size):
        batch = queries[i:i + effective_batch_size]
        batch_num = (i // effective_batch_size) + 1
        total_batches = (total_queries + effective_batch_size - 1) // effective_batch_size
        
        request_batch = list(batch)
        if anchor:
            request_batch.append(anchor)
            
        print(f"  Batch {batch_num}/{total_batches}: {', '.join(batch)}")
        
        response = client.fetch_interest_over_time(request_batch)
        
        if "error" in response:
            print(f"    Error: {response['error']}")
            continue
            
        timeline = response.get("interest_over_time", {}).get("timeline_data", [])
        if not timeline:
            print(f"    No timeline data found for batch {batch_num}")
            continue
            
        # Determine scaling factor
        multiplier = 1.0
        if anchor:
            anchor_idx = len(request_batch) - 1
            # Calculate anchor max in this batch to find multiplier
            anchor_values = []
            for point in timeline:
                if "values" in point and anchor_idx < len(point["values"]):
                    val = point["values"][anchor_idx].get("value", 0)
                    anchor_values.append(float(val) if isinstance(val, (int, float)) else 0.0)
            
            if anchor_values:
                current_anchor_max = max(anchor_values)
                if reference_anchor_val is None:
                    reference_anchor_val = current_anchor_max
                    print(f"    [Scaling] Reference Anchor Max: {reference_anchor_val}")
                
                multiplier = get_scaling_multiplier(current_anchor_max, reference_anchor_val)
                if multiplier != 1.0:
                    print(f"    [Scaling] Applying x{multiplier:.4f} to this batch")

        # Extract values for each query in batch
        for idx, query in enumerate(batch):
            query_points = []
            for point in timeline:
                if "values" in point and idx < len(point["values"]):
                    val = point["values"][idx].get("value")
                    # Scale the value if necessary
                    if isinstance(val, (int, float)):
                        scaled_val = round(val * multiplier, 2)
                    elif isinstance(val, str) and "<" in val:
                        scaled_val = round(0.5 * multiplier, 2)
                    else:
                        scaled_val = 0.0
                        
                    query_points.append({
                        "date": point.get("date"),
                        "timestamp": point.get("timestamp"),
                        "value": scaled_val
                    })
            timeseries_map[query] = query_points

    # Enrich original data with timeseries
    results = []
    enriched_count = 0
    for item in validated_data:
        query = item["query"]
        if query in timeseries_map:
            item["timeseries"] = timeseries_map[query]
            enriched_count += 1
        results.append(item)

    # Ensure output/timeseries directory exists
    output_dir = Path("output/timeseries")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find next available filename
    n = 1
    while (output_dir / f"timeseries{n}.json").exists():
        n += 1
    output_path = output_dir / f"timeseries{n}.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"\nTimeseries analysis complete! Saved {enriched_count} results to {output_path}")
    return output_path
