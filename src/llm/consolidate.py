from typing import List, Dict, Tuple
from src.llm.query_llm import query_llm


def generate_consolidated_queries(num_runs: int, mode: str = "both") -> List[str]:
    """
    Run the LLM multiple times and consolidate all queries, removing duplicates.
    
    Args:
        num_runs: Number of times to query the LLM
        mode: Generation mode passed to query_llm ("head", "tail", or "both")
        
    Returns:
        A deduplicated list of all queries from all runs
    """
    all_queries = []
    
    for i in range(num_runs):
        print(f"Run {i+1}/{num_runs}...")
        queries = query_llm(mode=mode)
        all_queries.extend(queries)
        print(f"  Generated {len(queries)} queries")
    
    print(f"\nTotal queries before deduplication: {len(all_queries)}")
    
    # Remove duplicates (case-insensitive) while preserving order
    unique_queries = _deduplicate_queries(all_queries)
    
    print(f"Unique queries after deduplication: {len(unique_queries)}")
    print(f"Duplicates removed: {len(all_queries) - len(unique_queries)}")
    
    return unique_queries


def generate_consolidated_clusters(
    num_runs: int, 
    similarity_threshold: float = 0.75,
    mode: str = "both",
) -> List[Tuple[str, str]]:
    """
    Run the LLM multiple times, parse clusters, and consolidate using semantic similarity.
    
    Args:
        num_runs: Number of times to query the LLM
        similarity_threshold: Cosine similarity threshold for merging clusters (0-1)
        mode: Generation mode passed to build_prompt ("head", "tail", or "both")
        
    Returns:
        List of (cluster_title, query) tuples
    """
    from src.llm.query_llm import _call_replicate
    from src.llm.assemble_prompts import build_prompt
    from src.llm.parse_clusters import parse_clustered_output, flatten_clusters
    from src.llm.semantic_clustering import consolidate_with_semantic_clustering
    
    all_clusters = []
    
    for i in range(num_runs):
        print(f"Run {i+1}/{num_runs}...")
        
        # Get raw LLM output
        prompt = build_prompt(mode=mode)
        raw_text = _call_replicate(prompt)
        
        # Parse into clusters
        clusters = parse_clustered_output(raw_text)
        all_clusters.extend(clusters)
        
        total_queries = sum(len(c['queries']) for c in clusters)
        print(f"  Generated {len(clusters)} clusters with {total_queries} queries")
    
    print(f"\nTotal clusters before consolidation: {len(all_clusters)}")
    
    # Consolidate semantically similar clusters
    consolidated_clusters = consolidate_with_semantic_clustering(
        all_clusters, 
        similarity_threshold=similarity_threshold
    )
    
    total_queries = sum(len(c['queries']) for c in consolidated_clusters)
    print(f"Total queries after consolidation: {total_queries}")
    
    # Flatten to (cluster, query) tuples
    return flatten_clusters(consolidated_clusters)


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

