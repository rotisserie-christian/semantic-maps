import sys
import json
import csv
import argparse
from pathlib import Path
from typing import List, Dict

# import from src
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
except ImportError:
    print("Error: sentence-transformers or sklearn not installed.")
    sys.exit(1)

def load_json(path: Path) -> List[Dict]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path: Path, data: List[Dict]):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Add queries from CSV to existing JSON clusters.")
    parser.add_argument("target_json", help="Filename of the JSON in /output")
    args = parser.parse_args()

    json_path = project_root / "output" / args.target_json
    if not json_path.exists():
        print(f"Error: Target JSON file {json_path} not found.")
        return

    csv_path = project_root / "src" / "utils" / "queries.csv"
    if not csv_path.exists():
        print(f"Error: queries.csv not found at {csv_path}")
        return

    # Load data
    clusters = load_json(json_path)
    new_queries = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                query = row[0].strip()
                if query and query != "Type here.":
                    new_queries.append(query)

    if not new_queries:
        print("No new queries to add.")
        return

    # Filter out existing queries
    existing_queries_lower = set()
    for c in clusters:
        for q in c['queries']:
            existing_queries_lower.add(q.lower().strip())

    to_add = [q for q in new_queries if q.lower().strip() not in existing_queries_lower]
    
    if not to_add:
        print("All queries in CSV already exist in the target JSON.")
        return

    print(f"Adding {len(to_add)} queries...")

    # Load model
    print("Loading sentence-transformers model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Prepare cluster titles and embeddings
    cluster_titles = [c['cluster'] for c in clusters]
    title_embeddings = model.encode(cluster_titles)
    
    # Process each new query
    query_embeddings = model.encode(to_add)
    
    # Calculate similarities
    similarities = cosine_similarity(query_embeddings, title_embeddings)
    
    for i, query in enumerate(to_add):
        # Find best matching cluster
        best_match_idx = np.argmax(similarities[i])
        best_cluster = clusters[best_match_idx]
        
        best_cluster['queries'].append(query)
        print(f"  Added '{query}' to cluster '{best_cluster['cluster']}' (score: {similarities[i][best_match_idx]:.4f})")

    # Save results
    save_json(json_path, clusters)
    print(f"\nSuccessfully updated {json_path}")

if __name__ == "__main__":
    main()
