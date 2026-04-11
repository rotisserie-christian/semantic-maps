from typing import List, Dict, Any

def extract_timeseries_values(timeseries: List[Dict[str, Any]]) -> List[float]:
    """
    Extract numerical values from a timeseries list of dictionaries.
    Handles "<1" or similar string values by converting to 0.5.
    """
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
    return values

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
    
    # Calculate sums
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x_sq = sum(xi**2 for xi in x)
    
    denominator = (n * sum_x_sq) - (sum_x**2)
    if denominator == 0:
        return 0.0
        
    slope = (n * sum_xy - sum_x * sum_y) / denominator
    return round(slope, 4)

def get_scaling_multiplier(current_batch_anchor_val: float, reference_anchor_val: float) -> float:
    """
    Calculates the multiplier needed to normalize the current batch to the reference batch.
    
    Args:
        current_batch_anchor_val: the anchor's metric (e.g. max_interest) in the current batch
        reference_anchor_val: the anchor's metric in the reference (first) batch
        
    Returns:
        A multiplier (float). If the anchor is 0 in the current batch, returns 1.0.
    """
    if not current_batch_anchor_val or current_batch_anchor_val == 0:
        return 1.0
    return reference_anchor_val / current_batch_anchor_val

def rebase_metrics(metrics: Dict[str, Any], multiplier: float) -> Dict[str, Any]:
    """
    Applies a multiplier to interest metrics to normalize them across batches.
    
    Args:
        metrics: Dict containing avg_interest, max_interest, etc.
        multiplier: The scaling factor to apply
        
    Returns:
        Updated metrics dict with rebased values.
    """
    if multiplier == 1.0:
        return metrics
        
    rebased = metrics.copy()
    rebased["avg_interest"] = round(metrics.get("avg_interest", 0) * multiplier, 2)
    rebased["max_interest"] = round(metrics.get("max_interest", 0) * multiplier, 2)
    rebased["min_interest"] = round(metrics.get("min_interest", 0) * multiplier, 2)
    rebased["is_normalized"] = True
    rebased["normalization_multiplier"] = round(multiplier, 4)
    
    return rebased
