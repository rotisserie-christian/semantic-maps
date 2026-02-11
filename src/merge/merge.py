import json
from pathlib import Path
from typing import List, Dict, Any
from src.utils.calculations import calculate_slope, extract_timeseries_values

def run_merge(timeseries_path_str: str, slope_path_str: str) -> Path:
    """
    Merges timeseries data into a slope file.
    Calculates slope for queries in timeseries file and updates/adds them to slope file.
    """
    timeseries_path = Path(timeseries_path_str)
    slope_path = Path(slope_path_str)

    if not timeseries_path.exists():
        raise FileNotFoundError(f"Timeseries file not found: {timeseries_path}")
    
    slope_data = []
    if slope_path.exists():
        try:
            with open(slope_path, "r", encoding="utf-8") as f:
                slope_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse {slope_path}. Starting with empty data.")
            slope_data = []
    else:
        print(f"Slope file {slope_path} not found. Creating new file.")

    with open(timeseries_path, "r", encoding="utf-8") as f:
        timeseries_data = json.load(f)

    # Convert slope list to dict for merging, keyed by query
    slope_map = {item["query"]: item for item in slope_data if "query" in item}

    merged_count = 0
    updated_count = 0

    print(f"Processing timeseries data from {timeseries_path}...")

    for item in timeseries_data:
        query = item.get("query")
        if not query:
            continue

        ts = item.get("timeseries", [])
        if not ts:
             # If no timeseries data, skip or set 0? 
             # run_slope_analysis sets 0.0
             slope_val = 0.0
        else:
             values = extract_timeseries_values(ts)
             slope_val = calculate_slope(values)
        
        entry = {
            "query": query,
            "cluster": item.get("cluster"),
            "slope": slope_val,
            "avg_interest": item.get("metrics", {}).get("avg_interest"),
            "max_interest": item.get("metrics", {}).get("max_interest")
        }

        if query in slope_map:
            updated_count += 1
        else:
            merged_count += 1
            
        slope_map[query] = entry

    # Convert back to list
    final_results = list(slope_map.values())
    
    # Sort by slope descending
    final_results.sort(key=lambda x: x.get("slope", 0), reverse=True)

    # Ensure directory exists
    slope_path.parent.mkdir(parents=True, exist_ok=True)

    # Save
    with open(slope_path, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)

    print(f"\nMerge complete!")
    print(f"  Added {merged_count} new queries.")
    print(f"  Updated {updated_count} existing queries.")
    print(f"  Total queries in slope file: {len(final_results)}")
    print(f"Saved results to: {slope_path}")
    
    return slope_path
