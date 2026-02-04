from src.llm.query_llm import query_llm
from src.llm.save_output import save_queries_to_csv


def main() -> None:
    """
    - builds a prompt for the default profile
    - queries the LLM
    - saves the resulting queries to output/searchtermsN.csv
    """
    queries = query_llm()
    path = save_queries_to_csv(queries)

    print(f"Generated {len(queries)} queries.")
    print(f"Saved to {path}")


if __name__ == "__main__":
    main()

