from . import query_length, complexity


def get_all_prompts(profile: dict) -> dict[str, str]:
    """Return all prompt blocks for the given profile."""
    return {
        "query_length": query_length.get_prompt(profile),
        "complexity": complexity.get_prompt(profile),
        # reformulation, specificity, patience, word_choice
    }

