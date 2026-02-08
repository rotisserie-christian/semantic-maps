import argparse
from src.llm.query_llm import query_llm
from src.llm.consolidate import generate_consolidated_queries
from src.llm.save_output import save_queries_to_csv


def main() -> None:
    """
    - builds a prompt for the default profile
    - queries the LLM (optionally multiple times with consolidation)
    - saves the resulting queries to output/searchtermsN.csv
    """
    parser = argparse.ArgumentParser(
        description="Generate search queries based on user profile"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of times to run the LLM and consolidate results (default: 1)"
    )
    
    args = parser.parse_args()
    
    # Generate queries (single run or consolidated multiple runs)
    if args.runs > 1:
        print(f"Running LLM {args.runs} times with consolidation...\n")
        queries = generate_consolidated_queries(args.runs)
    else:
        queries = query_llm()
    
    # Save to CSV
    path = save_queries_to_csv(queries)

    print(f"\nGenerated {len(queries)} queries.")
    print(f"Saved to {path}")


if __name__ == "__main__":
    main()

