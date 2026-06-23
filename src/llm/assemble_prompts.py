from typing import Dict, Optional, List
from src.config import profile as default_profile
from src.heuristics.prompts import get_all_prompts


def build_prompt(profile_override: Optional[Dict[str, object]] = None) -> str:
    """
    Build the full LLM prompt

    If profile_override is provided, it is merged on top of the default profile
    from config.py.
    """
    profile = default_profile.copy()
    if profile_override:
        profile.update(profile_override)

    behaviour_blocks = get_all_prompts(profile)

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

    sections.append(
        """
        Task:
        Generate a diverse list of search queries that this user might realistically type, 
        given their profile and the behaviour described above.

        - Use the described query length, complexity, specificity, reformulation style, 
        and word choice.
        - Focus on queries that match the user's goals and constraints.
        - Cluster the queries by search intent.
        - Each cluster must have a concise title followed by a colon, then the queries on separate lines.
        - Return as many queries as possible, try to cover all possible angles.
        - Include both specific and generic queries.

        Format:
        Cluster Title 1:
        query 1
        query 2

        Cluster Title 2:
        query 3
        query 4
        """
    )

    return "\n\n".join(sections)


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