from typing import List, Dict, Optional
from statistics import mean


def calculate_interest_metrics(timeline_data: List[Dict]) -> Dict:
    """
    Args:
        timeline_data: List of {date, timestamp, values} or {date, timestamp, value} dicts from API
        
    Returns:
        Dict with avg_interest, max_interest, min_interest, trend_direction, data_points
    """
    if not timeline_data:
        return {
            "avg_interest": 0,
            "max_interest": 0,
            "min_interest": 0,
            "trend_direction": "unknown",
            "data_points": 0
        }
    
    # Extract all values (handle multiple queries in timeline)
    all_values = []
    for point in timeline_data:
        if "values" in point:
            # Multiple queries: values is a list of dicts with 'value' key
            all_values.extend([v["value"] for v in point["values"] if "value" in v])
        elif "value" in point:
            # Single query: direct value
            all_values.append(point["value"])
    
    if not all_values:
        return {
            "avg_interest": 0,
            "max_interest": 0,
            "min_interest": 0,
            "trend_direction": "unknown",
            "data_points": 0
        }
    
    avg = mean(all_values)
    max_val = max(all_values)
    min_val = min(all_values)
    
    # trend direction (compare first half vs second half)
    mid = len(all_values) // 2
    if mid > 0:
        first_half = mean(all_values[:mid])
        second_half = mean(all_values[mid:])
        
        if second_half > first_half * 1.1:
            direction = "rising"
        elif second_half < first_half * 0.9:
            direction = "falling"
        else:
            direction = "stable"
    else:
        direction = "stable"
    
    return {
        "avg_interest": round(avg, 2),
        "max_interest": max_val,
        "min_interest": min_val,
        "trend_direction": direction,
        "data_points": len(all_values)
    }


def extract_query_interest(
    api_response: Dict,
    query: str
) -> Optional[Dict]:
    """
    Args:
        api_response: Raw API response from fetch_interest_over_time
        query: The specific query to extract data for (used for logging/debugging)
        
    Returns:
        Interest metrics dict or None if not found
    """
    if "error" in api_response:
        return None
    
    timeline = api_response.get("interest_over_time", {}).get("timeline_data", [])
    
    if not timeline:
        return None
    
    # For batched queries, return aggregate metrics across all queries in batch
    # For single query, it's the metrics for that specific query
    return calculate_interest_metrics(timeline)


def extract_query_interest_from_batch(
    api_response: Dict,
    query: str,
    query_index: int
) -> Optional[Dict]:
    """
    Extract interest metrics for a specific query from a batched API response.
    
    Args:
        api_response: Raw API response from fetch_interest_over_time (batched)
        query: The specific query to extract data for
        query_index: Index of the query in the batch (0-4)
        
    Returns:
        Interest metrics dict or None if not found
    """
    if "error" in api_response:
        return None
    
    # Find the timeline data
    timeline = api_response.get("interest_over_time", {}).get("timeline_data", [])
    
    if not timeline:
        return None
    
    # Extract values for specific query from batched response
    query_values = []
    for point in timeline:
        if "values" in point and isinstance(point["values"], list):
            # Batched response: values is a list of dicts
            if query_index < len(point["values"]):
                value_dict = point["values"][query_index]
                if "value" in value_dict:
                    query_values.append({
                        "date": point.get("date"),
                        "timestamp": point.get("timestamp"),
                        "value": value_dict["value"]
                    })
    
    if not query_values:
        # Fallback to aggregate if can't extract specific query
        return calculate_interest_metrics(timeline)
    
    return calculate_interest_metrics(query_values)