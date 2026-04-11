import json
from pathlib import Path
from typing import List, Dict
from src.utils.calculations import calculate_slope, extract_timeseries_values

def run_slope_analysis(input_json_path: str | Path) -> Path:
    """
    Calculate the slope for each query in a timeseries JSON file.
    Saves the results to output/slope/timeseriesslopeN.json
    """
    input_path = Path(input_json_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    print(f"Loading timeseries data from {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    
    for item in data:
        query = item.get("query")
        timeseries = item.get("timeseries", [])
        
        if not timeseries:
            print(f"  Warning: No timeseries data for query '{query}'")
            slope_val = 0.0
        else:
            # handle <1 if necessary
            values = extract_timeseries_values(timeseries)
            
            slope_val = calculate_slope(values)
            
        results.append({
            "query": query,
            "cluster": item.get("cluster"),
            "slope": slope_val,
            "avg_interest": item.get("metrics", {}).get("avg_interest"),
            "max_interest": item.get("metrics", {}).get("max_interest"),
            "is_normalized": item.get("metrics", {}).get("is_normalized", False)
        })

    # Sort by slope descending
    results.sort(key=lambda x: x["slope"], reverse=True)

    # Ensure output/slope directory exists
    output_dir = Path("output/slope")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find next available filename
    n = 1
    while (output_dir / f"timeseriesslope{n}.json").exists():
        n += 1
    output_path = output_dir / f"timeseriesslope{n}.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"\nSlope analysis complete! Calculated slopes for {len(results)} queries.")
    print(f"Saved results to: {output_path}")
    return output_path
