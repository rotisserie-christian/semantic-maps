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
from src.merge.merge import run_merge, run_merge_slope, run_prune
from src.utils.logger import get_logger

logger = get_logger(__name__)


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
    parser.add_argument(
        "--explore",
        type=str,
        default=None,
        metavar="VALIDATED_JSON",
        help="Fetch related queries for queries in a validated JSON file (e.g., output/validatedterms1.json)"
    )
    parser.add_argument(
        "--merge",
        nargs=2,
        metavar=("SEARCHTERMS_JSON", "VALIDATED_JSON"),
        help="Merge new queries from searchterms into validated file and optionally validate them"
    )
    parser.add_argument(
        "--merge-slope",
        nargs=2,
        metavar=("TIMESERIES_JSON", "SLOPE_JSON"),
        help="Merge slope results from a timeseries JSON file into a slope JSON file"
    )
    parser.add_argument(
        "--prune",
        nargs=2,
        metavar=("SEARCHTERMS_JSON", "SLOPE_JSON"),
        help="Remove queries found in a slope JSON file from a search terms JSON file"
    )


    
    parser.add_argument(
        "--anchor",
        type=str,
        default="free music maker",
        help="Anchor term for validation comparison (default: 'free music maker')"
    )

    
    args = parser.parse_args()
    
    # If validation mode, run validation and exit
    if args.validate:
        input_path = Path(args.validate)
        
        if not input_path.exists():
            logger.error(f"File not found: {input_path}")
            logger.info("Make sure you've generated queries first:\n  python main.py --runs 3")
            return
        
        logger.info("="*60)
        logger.info(f"VALIDATION: Validating {input_path}")
        if args.anchor:
            logger.info(f"Anchor term: {args.anchor}")
        logger.info("="*60)
        
        try:
            validated_path = run_validation(input_path, anchor=args.anchor)
            
            if validated_path:
                logger.info("="*60)
                logger.info("Validation complete!")
                logger.info("="*60)
                logger.info(f"Results saved to: {validated_path}")
        except Exception as e:
            logger.exception("Validation failed")
        
        return
    
    # If timeseries mode, run timeseries and exit
    if args.timeseries:
        input_path = Path(args.timeseries)
        
        if not input_path.exists():
            logger.error(f"File not found: {input_path}")
            return
            
        logger.info("="*60)
        logger.info(f"TIMESERIES: Fetching interest over time for {input_path}")
        logger.info("="*60)
        
        try:
            ts_path = run_timeseries(input_path, anchor=args.anchor)
            
            if ts_path:
                logger.info("="*60)
                logger.info("Timeseries analysis complete!")
                logger.info("="*60)
                logger.info(f"Results saved to: {ts_path}")
        except Exception as e:
            logger.exception("Timeseries analysis failed")
        
        return
    
    # If slope mode, run slope analysis and exit
    if args.slope:
        input_path = Path(args.slope)
        
        if not input_path.exists():
            logger.error(f"File not found: {input_path}")
            return
            
        logger.info("="*60)
        logger.info(f"SLOPE: Calculating rate of change for {input_path}")
        logger.info("="*60)
        
        try:
            slope_path = run_slope_analysis(input_path)
            
            if slope_path:
                logger.info("="*60)
                logger.info("Slope analysis complete!")
                logger.info("="*60)
                logger.info(f"Results saved to: {slope_path}")
        except Exception as e:
            logger.exception("Slope analysis failed")
        
        return

        # If explore mode, run exploration and exit
    if args.explore:
        input_path = Path(args.explore)
        
        if not input_path.exists():
            logger.error(f"File not found: {input_path}")
            return
            
        logger.info("="*60)
        logger.info(f"EXPLORE: Fetching related queries for {input_path}")
        logger.info("="*60)
        
        try:
            from src.explore import run_explore
            updated_path = run_explore(input_path)
            
            if updated_path:
                logger.info("="*60)
                logger.info("Exploration complete!")
                logger.info("="*60)
                logger.info(f"Updated file: {updated_path}")
                logger.info(f"Next steps:\n  - Review the updated file: {updated_path}\n  - Validate if needed: python main.py --validate {updated_path}")
        except Exception as e:
            logger.exception("Exploration failed")
        
        return


    # If merge mode, run merge and exit
    if args.merge:
        search_path_str, validated_path_str = args.merge
        
        logger.info("="*60)
        logger.info(f"MERGE: Merging new queries from {search_path_str} into {validated_path_str}")
        logger.info("="*60)
        
        try:
            merged_path = run_merge(search_path_str, validated_path_str)
            
            if merged_path:
                logger.info("="*60)
                logger.info("Merge complete!")
                logger.info("="*60)
                logger.info(f"Results saved to: {merged_path}")
        except Exception as e:
            logger.exception("Merge failed")
            
        return

    # If merge-slope mode, run merge-slope and exit
    if args.merge_slope:
        timeseries_path_str, slope_path_str = args.merge_slope
        
        logger.info("="*60)
        logger.info(f"MERGE-SLOPE: Merging {timeseries_path_str} into {slope_path_str}")
        logger.info("="*60)
        
        try:
            merged_path = run_merge_slope(timeseries_path_str, slope_path_str)
            
            if merged_path:
                logger.info("="*60)
                logger.info("Merge slope complete!")
                logger.info("="*60)
                logger.info(f"Results saved to: {merged_path}")
        except Exception as e:
            logger.exception("Merge slope failed")
            
        return

    # If prune mode, run prune and exit
    if args.prune:
        search_path_str, slope_path_str = args.prune
        
        logger.info("="*60)
        logger.info(f"PRUNE: Removing terms in {slope_path_str} from {search_path_str}")
        logger.info("="*60)
        
        try:
            pruned_path = run_prune(search_path_str, slope_path_str)
            
            if pruned_path:
                logger.info("="*60)
                logger.info("Pruning complete!")
                logger.info("="*60)
                logger.info(f"Results saved to: {pruned_path}")
        except Exception as e:
            logger.exception("Pruning failed")
            
        return


    
    # Generate queries
    if args.runs > 1:
        # Multiple runs
        logger.info(f"Running LLM {args.runs} times with semantic clustering (threshold={args.threshold})...")
        clustered_queries = generate_consolidated_clusters(args.runs, args.threshold)
        
        # Save in all three formats
        csv_path = save_clustered_queries_to_csv(clustered_queries)
        txt_path = save_clustered_queries_to_txt(clustered_queries)
        json_path = save_clustered_queries_to_json(clustered_queries)
        
        num_queries = len(clustered_queries)
        
        logger.info(f"Generated {num_queries} queries.")
        logger.info(f"Saved to:\n  - {csv_path}\n  - {txt_path}\n  - {json_path}")
    else:
        # Single run
        queries = query_llm()
        path = save_queries_to_csv(queries)
        num_queries = len(queries)
        
        logger.info(f"Generated {num_queries} queries.")
        logger.info(f"Saved to {path}")


if __name__ == "__main__":
    main()