from typing import List, Dict, Tuple
import re


def parse_clustered_output(raw_text: str) -> List[Dict[str, object]]:
    """
    Parse LLM output that contains cluster titles and queries.
    
    Expected format:
        Cluster Title 1:
        query 1
        query 2
        
        Cluster Title 2:
        query 3
        query 4
    
    Returns:
        List of dicts with 'cluster' and 'queries' keys
    """
    clusters = []
    current_cluster = None
    current_queries = []
    
    for line in raw_text.splitlines():
        stripped = line.strip()
        
        if not stripped:
            continue
        
        if _is_cluster_title(stripped):
            if current_cluster and current_queries:
                clusters.append({
                    'cluster': current_cluster,
                    'queries': current_queries.copy()
                })
            
            current_cluster = _clean_cluster_title(stripped)
            current_queries = []
        else:
            # query
            cleaned_query = _clean_query(stripped)
            if cleaned_query and current_cluster:
                current_queries.append(cleaned_query)
    
    # last cluster
    if current_cluster and current_queries:
        clusters.append({
            'cluster': current_cluster,
            'queries': current_queries.copy()
        })
    
    return clusters


def _is_cluster_title(line: str) -> bool:
    """
    Heuristics to detect if a line is a cluster title.
    
    Returns True if:
    - Ends with a colon
    - Is relatively short (< 80 chars)
    - Doesn't look like a search query (no question words at start)
    """
    if line.endswith(':'):
        return True
    
    # Check if it's all caps or title case and short
    if len(line) < 80 and (line.isupper() or line.istitle()):
        # Make sure it's not a query starting with question words
        query_starters = ['how', 'what', 'where', 'when', 'why', 'who', 'which']
        first_word = line.split()[0].lower() if line.split() else ''
        if first_word not in query_starters:
            return True
    
    return False


def _clean_cluster_title(title: str) -> str:
    """Remove trailing colons and extra whitespace from cluster titles."""
    return title.rstrip(':').strip()


def _clean_query(query: str) -> str:
    """
    Clean up a query string.
    
    Removes numbering, bullets, and extra whitespace.
    """
    # Strip off numbering if present
    if query[:2].isdigit() and len(query) > 2:
        rest = query[2:].lstrip('.). \t')
        if rest:
            query = rest
    
    # Remove bullet points
    query = re.sub(r'^[-•*]\s+', '', query)
    
    return query.strip()


def flatten_clusters(clusters: List[Dict[str, object]]) -> List[Tuple[str, str]]:
    """
    Flatten clustered data into (cluster_title, query) tuples.
    
    Args:
        clusters: List of dicts with 'cluster' and 'queries' keys
        
    Returns:
        List of (cluster_title, query) tuples
    """
    flattened = []
    for cluster_data in clusters:
        cluster_title = cluster_data['cluster']
        for query in cluster_data['queries']:
            flattened.append((cluster_title, query))
    
    return flattened
