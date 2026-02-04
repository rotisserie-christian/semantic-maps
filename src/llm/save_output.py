from __future__ import annotations
from pathlib import Path
from typing import Iterable, List
import csv


def _next_output_path(output_dir: Path) -> Path:
    """
    Return the next available CSV path, numbered sequentially
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    n = 1
    while True:
        candidate = output_dir / f"searchterms{n}.csv"
        if not candidate.exists():
            return candidate
        n += 1


def save_queries_to_csv(
    queries: Iterable[str],
    output_root: Path | str = "output",
) -> Path:
    """
    Write queries to a new CSV file 

    The file is named `searchtermsN.csv` where N is the first positive integer
    that doesn't already exist

    Returns:
        The Path of the CSV file that was written
    """
    output_dir = Path(output_root)
    output_path = _next_output_path(output_dir)

    # Normalize to a concrete list so it can be inspected
    query_list: List[str] = [q for q in queries if q]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["query"])
        for q in query_list:
            writer.writerow([q])

    return output_path