from . import query_length, complexity, reformulation, specificity, patience, word_choice


def get_all_prompts(profile: dict) -> dict[str, str]:
    """Return all prompt blocks for the given profile"""
    return {
        "query_length": query_length.get_prompt(profile),
        "complexity": complexity.get_prompt(profile),
        "reformulation": reformulation.get_prompt(profile),
        "specificity": specificity.get_prompt(profile),
        "patience": patience.get_prompt(profile),
        "word_choice": word_choice.get_prompt(profile),
    }

