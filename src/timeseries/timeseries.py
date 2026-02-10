import json
from pathlib import Path
from typing import List, Dict
from ..validate.fetch_trends import TrendsAPIClient
from ..validate.config import serpapi_config

def load_validated_queries(json_path: Path) -> List[Dict]:
    """Load queries from a validated search terms JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_timeseries(input_json_path: str | Path) -> Path:
    """
    Fetch interest over time (timeseries) for queries in a validated JSON file.
    Saves the result to output/timeseries/timeseriesN.json.
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
    batch_size = serpapi_config.get("batch_size", 5)
    
    timeseries_map = {}
    total_queries = len(queries)
    
    print(f"Fetching timeseries for {total_queries} queries in batches of {batch_size}...")
    
    for i in range(0, total_queries, batch_size):
        batch = queries[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_queries + batch_size - 1) // batch_size
        
        print(f"  Batch {batch_num}/{total_batches}: {', '.join(batch)}")
        
        response = client.fetch_interest_over_time(batch)
        
        if "error" in response:
            print(f"    Error: {response['error']}")
            continue
            
        timeline = response.get("interest_over_time", {}).get("timeline_data", [])
        if not timeline:
            print(f"    No timeline data found for batch {batch_num}")
            continue
            
        # Extract values for each query in batch
        for idx, query in enumerate(batch):
            query_points = []
            for point in timeline:
                if "values" in point and idx < len(point["values"]):
                    val = point["values"][idx].get("value")
                    query_points.append({
                        "date": point.get("date"),
                        "timestamp": point.get("timestamp"),
                        "value": val
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
