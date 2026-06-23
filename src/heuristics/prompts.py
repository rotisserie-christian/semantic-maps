from . import query_length, complexity, reformulation, specificity, word_choice

HEAD_HEURISTICS = ("word_choice", "reformulation")
TAIL_HEURISTICS = ("query_length", "complexity", "specificity")


def get_all_prompts(profile: dict, mode: str = "both") -> dict[str, str]:
    """
    Return prompt blocks for the given profile, filtered by mode.

    Args:
        profile: The user profile dict.
        mode: "head" (head-term heuristics only), "tail" (long-tail
            heuristics only), or "both" (all heuristics, default).
    """
    all_prompts = {
        "query_length": query_length.get_prompt(profile),
        "complexity": complexity.get_prompt(profile),
        "reformulation": reformulation.get_prompt(profile),
        "specificity": specificity.get_prompt(profile),
        "word_choice": word_choice.get_prompt(profile),
    }

    if mode == "head":
        keys = HEAD_HEURISTICS
    elif mode == "tail":
        keys = TAIL_HEURISTICS
    else:
        return all_prompts

    return {k: all_prompts[k] for k in keys}

