from typing import List, Dict, Any


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
    """
    rebased = metrics.copy()
    
    # Apply scaling
    if multiplier != 1.0:
        rebased["avg_interest"] = round(metrics.get("avg_interest", 0) * multiplier, 2)
        rebased["max_interest"] = round(metrics.get("max_interest", 0) * multiplier, 2)
        rebased["min_interest"] = round(metrics.get("min_interest", 0) * multiplier, 2)
    
    # Always set these if we are in a normalized pipeline
    rebased["is_normalized"] = True
    rebased["normalization_multiplier"] = round(multiplier, 4)
    
    return rebased
