import json
import sys
from pathlib import Path

def find_file(file_path: str) -> Path | None:
    """Try to find the file in multiple common locations."""
    path = Path(file_path)
    if path.exists():
        return path
    
    # Try relative to project root
    project_root = Path(__file__).parent.parent.parent
    root_path = project_root / file_path
    if root_path.exists():
        return root_path
    
    # Try common subdirectories in output
    search_dirs = [
        project_root / "output",
        project_root / "output" / "timeseries",
        project_root / "output" / "slope"
    ]
    
    filename = path.name
    for d in search_dirs:
        candidate = d / filename
        if candidate.exists():
            return candidate
            
    return None

def count_queries(file_path: str) -> int:
    path = find_file(file_path)
    if not path:
        print(f"Error: File '{file_path}' not found in current directory, project root, or output subdirectories.")
        return 0
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {path}")
        return 0
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return 0

    if not isinstance(data, list):
        print(f"Error: Expected a list at the top level of {path}")
        return 0

    count = 0
    for item in data:
        if not isinstance(item, dict):
            continue
        
        if "queries" in item and isinstance(item["queries"], list):
            count += len(item["queries"])
        elif "query" in item:
            count += 1
            
    return count

def main():
    if len(sys.argv) < 2:
        print("Usage: python lsq.py <json_file>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    count = count_queries(file_path)
    print(count)

if __name__ == "__main__":
    main()
