import argparse
from src.llm.query_llm import query_llm
from src.llm.consolidate import generate_consolidated_clusters
from src.llm.save_output import (
    save_queries_to_csv, 
    save_clustered_queries_to_csv,
    save_clustered_queries_to_txt,
    save_clustered_queries_to_json
)


def main() -> None:
    """
    - builds a prompt for the default profile
    - queries the LLM (optionally multiple times with semantic clustering)
    - saves the resulting queries to output/searchtermsN.csv
    """
    parser = argparse.ArgumentParser(
        description="Generate search queries based on user profile"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of times to run the LLM with semantic clustering (default: 1)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Similarity threshold for merging clusters when using --runs (0-1, default: 0.75)"
    )
    
    args = parser.parse_args()
    
    # Generate queries
    if args.runs > 1:
        # Multiple runs: Use semantic clustering with cluster consolidation
        print(f"Running LLM {args.runs} times with semantic clustering (threshold={args.threshold})...\n")
        clustered_queries = generate_consolidated_clusters(args.runs, args.threshold)
        
        # Save in all three formats
        csv_path = save_clustered_queries_to_csv(clustered_queries)
        txt_path = save_clustered_queries_to_txt(clustered_queries)
        json_path = save_clustered_queries_to_json(clustered_queries)
        
        num_queries = len(clustered_queries)
        
        print(f"\nGenerated {num_queries} queries.")
        print(f"Saved to:")
        print(f"  - {csv_path}")
        print(f"  - {txt_path}")
        print(f"  - {json_path}")
    else:
        # Single run
        queries = query_llm()
        path = save_queries_to_csv(queries)
        num_queries = len(queries)
        
        print(f"\nGenerated {num_queries} queries.")
        print(f"Saved to {path}")


if __name__ == "__main__":
    main()




