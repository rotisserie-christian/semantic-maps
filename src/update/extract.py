import json
from pathlib import Path
from typing import List, Dict, Tuple

def extract_queries_from_any(input_path: str | Path) -> List[Tuple[str, str]]:
    """
    Extracts (cluster, query) tuples from any of the profile's output formats:
    - searchtermsN.json (Discovery)
    - validatedtermsN.json (Validation)
    - timeseriesN.json (Timeseries)
    - timeseriesslopeN.json (Slope)
    
    Returns:
        List of (cluster, query) tuples
    """
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    queries = []
    
    # Handle list-based formats (most common)
    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
                
            cluster = item.get("cluster", "unknown")
            query = item.get("query")
            
            # Discovery format (clustered_queries) often has "queries" list
            if "queries" in item and isinstance(item["queries"], list):
                for q in item["queries"]:
                    queries.append((cluster, q))
            # Standard flattened format
            elif query:
                queries.append((cluster, query))
                
    return list(dict.fromkeys(queries)) # Deduplicate
