import argparse
from pathlib import Path
from src.llm.query_llm import query_llm
from src.llm.consolidate import generate_consolidated_clusters
from src.llm.save_output import (
    save_queries_to_csv, 
    save_clustered_queries_to_csv,
    save_clustered_queries_to_txt,
    save_clustered_queries_to_json
)
from src.validate import run_validation
from src.timeseries import run_timeseries
from src.slope import run_slope_analysis




def main() -> None:
    """
    - builds a prompt for the default profile
    - queries the LLM (optionally multiple times with semantic clustering)
    - saves the resulting queries to output/searchtermsN.csv
    - optionally validates queries with Google Trends data
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
    parser.add_argument(
        "--validate",
        type=str,
        default=None,
        metavar="JSON_FILE",
        help="Validate queries from JSON file using Google Trends (e.g., output/searchterms1.json)"
    )
    parser.add_argument(
        "--timeseries",
        type=str,
        default=None,
        metavar="VALIDATED_JSON",
        help="Fetch interest over time for queries in a validated JSON file (e.g., output/validatedterms1.json)"
    )
    parser.add_argument(
        "--slope",
        type=str,
        default=None,
        metavar="TIMESERIES_JSON",
        help="Calculate rate of change for queries in a timeseries JSON file (e.g., output/timeseries/timeseries1.json)"
    )


    
    args = parser.parse_args()
    
    # If validation mode, run validation and exit
    if args.validate:
        input_path = Path(args.validate)
        
        if not input_path.exists():
            print(f"Error: File not found: {input_path}")
            print("\nMake sure you've generated queries first:")
            print("  python main.py --runs 3")
            return
        
        print("="*60)
        print(f"VALIDATION: Validating {input_path}")
        print("="*60 + "\n")
        
        try:
            validated_path = run_validation(input_path)
            
            if validated_path:
                print(f"\n{'='*60}")
                print("Validation complete!")
                print("="*60)
                print(f"Results saved to: {validated_path}")
        except Exception as e:
            print(f"\nValidation failed: {e}")
            import traceback
            traceback.print_exc()
        
        return
    
    # If timeseries mode, run timeseries and exit
    if args.timeseries:
        input_path = Path(args.timeseries)
        
        if not input_path.exists():
            print(f"Error: File not found: {input_path}")
            return
            
        print("="*60)
        print(f"TIMESERIES: Fetching interest over time for {input_path}")
        print("="*60 + "\n")
        
        try:
            ts_path = run_timeseries(input_path)
            
            if ts_path:
                print(f"\n{'='*60}")
                print("Timeseries analysis complete!")
                print("="*60)
                print(f"Results saved to: {ts_path}")
        except Exception as e:
            print(f"\nTimeseries analysis failed: {e}")
            import traceback
            traceback.print_exc()
        
        return
    
    # If slope mode, run slope analysis and exit
    if args.slope:
        input_path = Path(args.slope)
        
        if not input_path.exists():
            print(f"Error: File not found: {input_path}")
            return
            
        print("="*60)
        print(f"SLOPE: Calculating rate of change for {input_path}")
        print("="*60 + "\n")
        
        try:
            slope_path = run_slope_analysis(input_path)
            
            if slope_path:
                print(f"\n{'='*60}")
                print("Slope analysis complete!")
                print("="*60)
                print(f"Results saved to: {slope_path}")
        except Exception as e:
            print(f"\nSlope analysis failed: {e}")
            import traceback
            traceback.print_exc()
        
        return


    
    # Generate queries
    if args.runs > 1:
        # Multiple runs
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