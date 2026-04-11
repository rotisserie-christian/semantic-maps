import json
from pathlib import Path
from src.update.extract import extract_queries_from_any
from src.validate.validate import validate_queries
from src.validate.save_validated import save_validated_json
from src.timeseries.timeseries import run_timeseries
from src.slope.slope import run_slope_analysis
from src.utils.logger import get_logger

logger = get_logger(__name__)

def run_full_update(input_path: str | Path, anchor: str = None) -> Path:
    """
    Orchestrates the full data refresh:
    1. Extracts queries from the source file
    2. Re-validates them against Trends (with normalization)
    3. Fetches new interest over time (Timeseries)
    4. Recalculates rate of change (Slope)
    """
    input_path = Path(input_path)
    logger.info(f"Starting update for terms in: {input_path}")
    
    # 1. Extraction
    try:
        queries = extract_queries_from_any(input_path)
        logger.info(f"Extracted {len(queries)} unique queries.")
    except Exception as e:
        logger.error(f"Failed to extract queries: {e}")
        return None
        
    # 2. Re-validation (Fresh averages and normalization multipliers)
    # We call validate_queries directly since we already have the list
    try:
        validated_results = validate_queries(queries, anchor=anchor)
        # We need to save this to disk because the next steps in the pipeline 
        # (timeseries, slope) are currently file-bound.
        validated_file = save_validated_json(validated_results)
        logger.info(f"Validation step complete. Saved to: {validated_file}")
    except Exception as e:
        logger.error(f"Validation step failed: {e}")
        return None
        
    # 3. Fresh Timeseries
    try:
        timeseries_file = run_timeseries(validated_file, anchor=anchor)
        logger.info(f"Timeseries step complete. Saved to: {timeseries_file}")
    except Exception as e:
        logger.error(f"Timeseries step failed: {e}")
        return None
        
    # 4. Final Slope Analysis
    try:
        slope_file = run_slope_analysis(timeseries_file)
        logger.info(f"Slope calculation complete. Saved to: {slope_file}")
    except Exception as e:
        logger.error(f"Slope step failed: {e}")
        return None
        
    # 5. Move/Rename result to updated directory
    output_dir = Path("output/updated")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    update_num = 1
    while (output_dir / f"updatedterms{update_num}.json").exists():
        update_num += 1
    
    final_output_path = output_dir / f"updatedterms{update_num}.json"
    
    # Move the final slope results to its permanent home
    Path(slope_file).rename(final_output_path)
    
    # Clean up intermediate files
    try:
        # Path(validated_file).unlink() # Optional: keep for debugging
        # Path(timeseries_file).unlink()
        pass
    except:
        pass
        
    logger.info("="*60)
    logger.info(f"UPDATE SUCCESSFUL")
    logger.info(f"Final normalized snapshot: {final_output_path}")
    logger.info("="*60)
    
    return final_output_path
