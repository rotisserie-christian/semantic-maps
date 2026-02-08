from typing import List, Dict, Tuple
from datetime import datetime


def consolidate_validated_results(
    original_queries: List[Tuple[str, str]], # cluster, query
    interest_data: Dict[str, Dict], # query -> metrics
    related_queries: Dict[str, List[str]], # parent_query -> [related]
    related_interest: Dict[str, Dict], # related_query -> metrics
    interest_threshold: float,
    related_threshold: float
) -> List[Dict]:
    """
    Consolidate original and related queries into final validated output.
    
    Args:
        original_queries: List of (cluster, query) tuples from generated output
        interest_data: Interest metrics for original queries
        related_queries: Map of parent query to related queries
        related_interest: Interest metrics for related queries
        interest_threshold: Minimum interest for original queries
        related_threshold: Minimum interest for related queries
        
    Returns:
        List of validated query dicts with all metadata
    """
    validated = []
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Process original queries
    for cluster, query in original_queries:
        metrics = interest_data.get(query)
        
        if not metrics:
            continue
        
        if metrics["avg_interest"] >= interest_threshold:
            validated.append({
                "cluster": cluster,
                "query": query,
                "source": "generated",
                "metrics": metrics,
                "related_to": None,
                "timestamp": timestamp
            })
    
    # Process related queries
    for parent_query, related_list in related_queries.items():
        # Find parent's cluster
        parent_cluster = None
        for cluster, query in original_queries:
            if query == parent_query:
                parent_cluster = cluster
                break
        
        if not parent_cluster:
            continue
        
        for related_query in related_list:
            metrics = related_interest.get(related_query)
            
            if not metrics:
                continue
            
            if metrics["avg_interest"] >= related_threshold:
                # Check if already exists, could be in original or from another parent
                if not any(v["query"] == related_query for v in validated):
                    validated.append({
                        "cluster": parent_cluster,
                        "query": related_query,
                        "source": "related",
                        "metrics": metrics,
                        "related_to": parent_query,
                        "timestamp": timestamp
                    })
    
    # Sort by avg_interest descending
    validated.sort(key=lambda x: x["metrics"]["avg_interest"], reverse=True)
    
    return validated