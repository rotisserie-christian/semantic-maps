import json
import re
from pathlib import Path

def clean_cluster_name(name):
    """Remove formatting artifacts from cluster name."""
    if not isinstance(name, str):
        return name
    
    # Remove markdown bold/italic markers
    cleaned = name.replace('*', '').replace('_', '')
    
    # Remove heading markers
    cleaned = cleaned.replace('#', '')
    
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    return cleaned

def main():
    file_path = Path('../../output/slope/timeseriesslope3.json')
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return

    print(f"Reading {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    count = 0
    for item in data:
        if 'cluster' in item:
            original = item['cluster']
            cleaned = clean_cluster_name(original)
            
            if original != cleaned:
                item['cluster'] = cleaned
                count += 1
                print(f"Cleaned: '{original}' -> '{cleaned}'")
    
    if count > 0:
        print(f"\nSaving {count} changes to {file_path}...")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Done!")
    else:
        print("\nNo changes needed.")

if __name__ == "__main__":
    main()
