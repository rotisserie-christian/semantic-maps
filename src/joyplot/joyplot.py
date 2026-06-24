import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..validate.fetch_trends import TrendsAPIClient

MAX_TERMS = 5


def load_joyplot_terms(csv_path: Path) -> List[str]:
    """
    Read terms from a joyplot CSV (one term per line).

    Trailing commas and blank lines are ignored. The list is capped at
    MAX_TERMS (Google Trends allows at most 5 queries per TIMESERIES call).
    """
    terms: List[str] = []

    with open(csv_path, "r", encoding="utf-8") as f:
        for row in csv.reader(f):
            for cell in row:
                term = cell.strip()
                if term:
                    terms.append(term)

    if len(terms) > MAX_TERMS:
        print(f"  [Warning] {len(terms)} terms found; using the first {MAX_TERMS}.")
        terms = terms[:MAX_TERMS]

    return terms


def _to_value(point_value: Dict) -> float:
    """
    Pull a numeric interest value from a timeline value entry.

    Prefers the API's pre-parsed `extracted_value`, falling back to parsing
    the raw `value` string (which can look like "<1").
    """
    if "extracted_value" in point_value and isinstance(point_value["extracted_value"], (int, float)):
        return float(point_value["extracted_value"])

    raw = point_value.get("value")
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str):
        cleaned = raw.replace("<", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    return 0.0


def reshape_timeline(api_response: Dict, terms: List[str]) -> List[Dict]:
    """
    Reshape a TIMESERIES response into one aligned series per term.

    Returns a list of {"query": str, "points": [{date, timestamp, value}]}.
    """
    timeline = api_response.get("interest_over_time", {}).get("timeline_data", [])

    series: Dict[str, List[Dict]] = {term: [] for term in terms}

    for point in timeline:
        date = point.get("date")
        timestamp = point.get("timestamp")

        if "values" in point and isinstance(point["values"], list):
            # Multi-query response: one entry per term, in request order
            for idx, value_entry in enumerate(point["values"]):
                query = value_entry.get("query")
                if query not in series and idx < len(terms):
                    query = terms[idx]
                if query in series:
                    series[query].append({
                        "date": date,
                        "timestamp": timestamp,
                        "value": _to_value(value_entry),
                    })
        elif "value" in point and terms:
            # Single-query response: value lives directly on the point
            series[terms[0]].append({
                "date": date,
                "timestamp": timestamp,
                "value": _to_value(point),
            })

    return [{"query": term, "points": series[term]} for term in terms]


def save_joyplot_json(
    series: List[Dict],
    terms: List[str],
    date_range: str,
    output_root: Path | str = "output",
) -> Path:
    """Write the per-term series to output/joyplot/joyplotdataN.json."""
    output_dir = Path(output_root) / "joyplot"
    output_dir.mkdir(parents=True, exist_ok=True)

    n = 1
    while True:
        output_path = output_dir / f"joyplotdata{n}.json"
        if not output_path.exists():
            break
        n += 1

    payload = {
        "date_range": date_range,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "terms": terms,
        "series": series,
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    return output_path


def run_joyplot(
    csv_path: str | Path,
    date: str = "today 5-y",
) -> Optional[Path]:
    """
    Fetch a single multi-term interest-over-time series for joyplot charting.

    Args:
        csv_path: Path to a CSV of terms (one per line, max 5).
        date: Google Trends date range (default "today 5-y").

    Returns:
        Path to the saved joyplotdataN.json file, or None on failure.
    """
    input_path = Path(csv_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    print(f"Loading joyplot terms from {input_path}...")
    terms = load_joyplot_terms(input_path)
    if not terms:
        print("No terms found in input file.")
        return None

    print(f"Terms ({len(terms)}): {', '.join(terms)}")

    print("Initializing SerpAPI client...")
    client = TrendsAPIClient()

    print(f"Fetching {date} interest data in a single request...")
    response = client.fetch_interest_over_time(terms, date=date)

    if "error" in response:
        print(f"Error fetching interest data: {response['error']}")
        return None

    series = reshape_timeline(response, terms)

    total_points = sum(len(s["points"]) for s in series)
    if total_points == 0:
        print("No timeline data returned for these terms.")
        return None

    output_path = save_joyplot_json(series, terms, date)
    print(f"\nJoyplot data saved to {output_path}")
    return output_path
