import json
from pathlib import Path
from typing import List, Dict

def calculate_slope(values: List[float]) -> float:
    """
    Calculate the linear slope (rate of change) of a series of values.
    Uses simple linear regression: m = (nΣxy - ΣxΣy) / (nΣx² - (Σx)²)
    """
    n = len(values)
    if n < 2:
        return 0.0
    
    # Use indices as x-values
    x = list(range(n))
    y = values
    
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x_sq = sum(xi**2 for xi in x)
    
    denominator = (n * sum_x_sq) - (sum_x**2)
    if denominator == 0:
        return 0.0
        
    slope = (n * sum_xy - sum_x * sum_y) / denominator
    return round(slope, 4)

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
            values = []
            for p in timeseries:
                val = p.get("value", 0)
                if isinstance(val, str):
                    if "<" in val:
                        values.append(0.5)
                    else:
                        try:
                            values.append(float(val))
                        except ValueError:
                            values.append(0.0)
                elif isinstance(val, (int, float)):
                    values.append(float(val))
                else:
                    values.append(0.0)
            
            slope_val = calculate_slope(values)
            
        results.append({
            "query": query,
            "cluster": item.get("cluster"),
            "slope": slope_val,
            "avg_interest": item.get("metrics", {}).get("avg_interest"),
            "max_interest": item.get("metrics", {}).get("max_interest")
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
