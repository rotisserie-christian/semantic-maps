from typing import Dict, Optional, List
from src.config import profile as default_profile
from src.heuristics.prompts import get_all_prompts


def build_prompt(
    profile_override: Optional[Dict[str, object]] = None,
    mode: str = "both",
) -> str:
    """
    Build the full LLM prompt

    If profile_override is provided, it is merged on top of the default profile
    from config.py.

    Args:
        profile_override: Dictionary to override the default user profile.
        mode: "head" (short, high-volume terms for Trends), "tail" (long-tail
            persona-modeling terms), or "both" (default).
    """
    profile = default_profile.copy()
    if profile_override:
        profile.update(profile_override)

    behaviour_blocks = get_all_prompts(profile, mode=mode)

    age_group = profile.get("age_group", "")
    domain_expertise = profile.get("domain_expertise", "")
    description = profile.get("description", "")

    # Core instructions + profile + research-backed behaviour blocks
    sections = []

    sections.append(
        """
        The task is to generate example search engine queries 
        for a user, based on their profile and empirically observed 
        search behaviour patterns.
        """
    )

    sections.append(
        f"User profile:\n"
        f"- Age group: {age_group}\n"
        f"- Domain expertise: {domain_expertise}\n"
        f"- Description: {description}"
    )

    sections.append("Search behaviour (summarised from research):")

    for name, text in behaviour_blocks.items():
        label = name.replace("_", " ").title()
        sections.append(f"{label}:\n{text}")

    sections.append(_build_task_block(mode))

    return "\n\n".join(sections)


def _build_task_block(mode: str) -> str:
    """Return the task instructions, tuned to the generation mode."""
    if mode == "head":
        guidance = """
        - Keep queries short (about 2-4 words) and the way a real person would
        actually type them, not generic one-word category labels.
        - Use the described reformulation style and word choice.
        - Stay head-friendly (avoid long "how to ... for ..." phrasing), but keep
        the short qualifiers that reveal this user's situation and intent, such
        as skill level, the problem they're stuck on, or free vs paid.
        - Capture what this specific user is actually trying to do, not just the
        most obvious term for the broad category.
        - Prefer phrasings real users search, balancing volume with intent.
        """
    elif mode == "tail":
        guidance = """
        - Use the described query length, complexity, and specificity.
        - Favor specific, narrowly-scoped phrasings (for example "how to ..."
        or "best ... for ...").
        - Focus on queries that match the user's goals and constraints.
        - Return as many queries as possible, try to cover all possible angles.
        """
    else:
        guidance = """
        - Use the described query length, complexity, specificity, reformulation
        style, and word choice.
        - Focus on queries that match the user's goals and constraints.
        - Return as many queries as possible, try to cover all possible angles.
        - Include both specific and generic queries.
        """

    return (
        "Task:\n"
        "Generate a list of search queries that this user might realistically "
        "type, given their profile and the behaviour described above.\n"
        f"{guidance}"
        "- Cluster the queries by search intent.\n"
        "- Each cluster must have a concise title followed by a colon, then the "
        "queries on separate lines.\n\n"
        "Format:\n"
        "Cluster Title 1:\n"
        "query 1\n"
        "query 2\n\n"
        "Cluster Title 2:\n"
        "query 3\n"
        "query 4\n"
    )


def build_review_prompt(review_texts: List[str]) -> str:
    """
    Build the prompt for semantic analysis of Google Maps reviews.
    """
    reviews_block = "\n".join([f"- {r}" for r in review_texts])
    
    return f"""
Act as a Senior Business Intelligence Analyst. Your goal is to identify every piece of specific feedback that is repeated across at least two different reviews.

REVIEWS:
{reviews_block}

TASK:
1. Scan every review and identify recurring semantic themes or specific feedback points.
2. Be exhaustive: If a piece of feedback (strength or weakness) appears in 2 or more reviews, it must be included as a cluster.
3. For each cluster, provide a 2-5 word label.
4. Categorize as "Strength" or "Weakness".
5. List the exact review snippets for every review that matches that cluster. Do not just provide a few examples; map every single matching review.

OUTPUT FORMAT (JSON):
[
  {{
    "feedback": "descriptive label",
    "type": "Strength/Weakness",
    "matches": ["exact snippet 1", "exact snippet 2", "exact snippet 3", ...]
  }}
]
"""