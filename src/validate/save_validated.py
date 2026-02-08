from pathlib import Path
import json
from typing import List, Dict


def _next_validated_path(output_dir: Path) -> Path:
    """
    Return the next available validatedtermsN.json path.
    
    Args:
        output_dir: Directory to save the file
        
    Returns:
        Path to the next available file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    n = 1
    while True:
        candidate = output_dir / f"validatedterms{n}.json"
        if not candidate.exists():
            return candidate
        n += 1


def save_validated_json(
    validated_queries: List[Dict],
    output_root: Path | str = "output"
) -> Path:
    """
    Args:
        validated_queries: List of validated query dicts
        output_root: Directory to save the file
        
    Returns:
        Path to the saved file
    """
    output_dir = Path(output_root)
    output_path = _next_validated_path(output_dir)
    
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(validated_queries, f, indent=2, ensure_ascii=False)
    
    return output_path