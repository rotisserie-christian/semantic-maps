import json
from pathlib import Path
from typing import List, Dict, Tuple

def run_merge(
    search_path_str: str,
    validated_path_str: str,
    validate_new: bool = True
) -> Path:
    """
    Merges new queries from a searchterms file into an existing validated file.

    Identifies queries in the searchterms file that don't already exist in the
    validated file, assigns them to the closest existing cluster using semantic
    similarity, optionally validates them via Google Trends, and saves the result
    to a new validatedtermsN.json file.

    Args:
        search_path_str: Path to a searchtermsN.json file
        validated_path_str: Path to an existing validatedtermsN.json file
        validate_new: If True, fetch Google Trends data for new queries before saving

    Returns:
        Path to the saved output file
    """
    search_path = Path(search_path_str)
    validated_path = Path(validated_path_str)

    if not search_path.exists():
        raise FileNotFoundError(f"Search terms file not found: {search_path}")
    if not validated_path.exists():
        raise FileNotFoundError(f"Validated terms file not found: {validated_path}")

    with open(search_path, "r", encoding="utf-8") as f:
        search_data = json.load(f)

    with open(validated_path, "r", encoding="utf-8") as f:
        validated_data = json.load(f)

    # Build lookup of existing queries for deduplication
    existing_queries = {
        item["query"].lower().strip()
        for item in validated_data
        if "query" in item
    }

    # Collect new candidates from search data
    new_candidates = []
    for cluster_item in search_data:
        for q in cluster_item.get("queries", []):
            if q.lower().strip() not in existing_queries:
                new_candidates.append(q)

    # Deduplicate within new candidates (preserve order)
    new_candidates = list(dict.fromkeys(new_candidates))

    if not new_candidates:
        print("No new queries found to merge.")
        return validated_path

    print(f"Found {len(new_candidates)} new queries to add.")

    # Assign each new query to the closest existing cluster
    assigned_queries = _assign_to_clusters(new_candidates, validated_data)

    if not validate_new:
        print("Skipping validation (validate_new=False). No output saved.")
        return validated_path

    from src.validate.validate import validate_queries
    from src.validate.save_validated import save_validated_json

    new_validated = validate_queries(assigned_queries)

    combined = validated_data + new_validated
    combined.sort(
        key=lambda x: x.get("metrics", {}).get("avg_interest", 0),
        reverse=True
    )

    output_path = save_validated_json(combined)
    print(f"\nMerge complete. Results saved to: {output_path}")
    return output_path


def _assign_to_clusters(
    queries: List[str],
    validated_data: List[Dict]
) -> List[Tuple[str, str]]:
    """
    Assigns each query to the most semantically similar existing cluster.

    Args:
        queries: List of new query strings to assign
        validated_data: Existing validated data to derive cluster names from

    Returns:
        List of (cluster, query) tuples
    """
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    unique_clusters = list(dict.fromkeys(
        item["cluster"] for item in validated_data if "cluster" in item
    )) or ["General"]

    print("Loading sentence-transformers model for clustering...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    cluster_embeddings = model.encode(unique_clusters)
    query_embeddings = model.encode(queries)
    similarities = cosine_similarity(query_embeddings, cluster_embeddings)

    assigned = []
    for i, query in enumerate(queries):
        best_cluster = unique_clusters[np.argmax(similarities[i])]
        assigned.append((best_cluster, query))
        print(f"  '{query}' → '{best_cluster}'")

    return assigned