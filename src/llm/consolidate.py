from typing import List
from src.llm.query_llm import query_llm


def generate_consolidated_queries(num_runs: int) -> List[str]:
    """
    Run the LLM multiple times and consolidate all queries, removing duplicates.
    
    Args:
        num_runs: Number of times to query the LLM
        
    Returns:
        A deduplicated list of all queries from all runs
    """
    all_queries = []
    
    for i in range(num_runs):
        print(f"Run {i+1}/{num_runs}...")
        queries = query_llm()
        all_queries.extend(queries)
        print(f"  Generated {len(queries)} queries")
    
    print(f"\nTotal queries before deduplication: {len(all_queries)}")
    
    # Remove duplicates (case-insensitive) while preserving order
    unique_queries = _deduplicate_queries(all_queries)
    
    print(f"Unique queries after deduplication: {len(unique_queries)}")
    print(f"Duplicates removed: {len(all_queries) - len(unique_queries)}")
    
    return unique_queries


def _deduplicate_queries(queries: List[str]) -> List[str]:
    """
    Remove duplicate queries using case-insensitive comparison.
    
    Preserves the order of first occurrence.
    
    Args:
        queries: List of query strings
        
    Returns:
        Deduplicated list of queries
    """
    seen = set()
    unique_queries = []
    
    for query in queries:
        # Normalize for comparison (lowercase, strip whitespace)
        normalized = query.lower().strip()
        
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique_queries.append(query)
    
    return unique_queries
