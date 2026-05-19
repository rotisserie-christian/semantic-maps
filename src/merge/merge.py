import json
from pathlib import Path
from typing import List, Dict, Any

def run_merge(search_path_str: str, validated_path_str: str) -> Path:
    """
    Merges queries from searchterms file into a validated file.
    Identifies new queries, clusters them, and optionally validates.
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

    # Extract existing queries from validated data for fast lookup
    existing_queries = {item["query"].lower().strip() for item in validated_data if "query" in item}
    
    # Extract all queries from search data
    all_new_candidates = []
    for cluster_item in search_data:
        queries = cluster_item.get("queries", [])
        for q in queries:
            if q.lower().strip() not in existing_queries:
                all_new_candidates.append(q)
    
    # Deduplicate within new candidates
    all_new_candidates = list(dict.fromkeys(all_new_candidates))

    if not all_new_candidates:
        print("No new queries found to merge.")
        return validated_path

    print(f"Found {len(all_new_candidates)} new queries to add.")

    # Clustering logic
    print("Loading sentence-transformers model for clustering...")
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Get unique clusters from validated data
    unique_clusters = list(dict.fromkeys([item["cluster"] for item in validated_data if "cluster" in item]))
    if not unique_clusters:
        # Fallback if validated data has no clusters
        unique_clusters = ["General"]
    
    cluster_embeddings = model.encode(unique_clusters)
    query_embeddings = model.encode(all_new_candidates)
    
    similarities = cosine_similarity(query_embeddings, cluster_embeddings)
    
    assigned_queries = []
    for i, query in enumerate(all_new_candidates):
        best_match_idx = np.argmax(similarities[i])
        best_cluster = unique_clusters[best_match_idx]
        assigned_queries.append((best_cluster, query))
        print(f"  Assigned '{query}' to cluster '{best_cluster}'")

    # Prompt for validation
    ans = input(f"\nDo you want to validate the {len(assigned_queries)} new queries? (y/n): ")
    
    if ans.lower() == 'y':
        from src.validate.validate import validate_queries
        from src.validate.save_validated import save_validated_json
        
        new_validated_data = validate_queries(assigned_queries)
        
        # Combine old data and new validated data
        final_results = validated_data + new_validated_data
        
        # Sort by avg_interest descending (if metrics exist)
        final_results.sort(key=lambda x: x.get("metrics", {}).get("avg_interest", 0), reverse=True)
        
        # Save to a new validated file
        output_path = save_validated_json(final_results)
        print(f"\nSuccessfully merged and validated results saved to: {output_path}")
        return output_path
    else:
        # Just add them without metrics if we wanted to save? 
        # But validated file format expects metrics. 
        # The user said "if y then perform the validate step". 
        # If 'n', maybe we don't do anything or just return without saving?
        # The prompt says "if y then perform... creating a new validatesearchtermsN file".
        # This implies it ONLY creates the file if validated.
        print("Merge cancelled (no validation performed).")
        return validated_path

