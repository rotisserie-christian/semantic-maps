# younger user = more specific phrasing
# high prior_task_knowledge = more specific even for older users

PROMPTS = {
    "vague":
    """
        This user tends to use broader, less specific search queries.
        They are more likely to type general topics or short phrases without many qualifiers.
        Generate search queries that are relatively high-level, avoiding very narrow or
        tightly-scoped phrasing unless it is absolutely necessary.
    """
    ,
    "moderate":
    """
        This user tends to use moderately specific search queries.
        They include some detail (for example, adding a goal or context) but do not always
        pin down all variables.
        Generate search queries that balance generality and precision: add a few clarifying
        words, but avoid making the query overly narrow.
    """
    ,
    "specific":
    """
        This user tends to use more specific, targeted search queries.
        They are comfortable adding detail such as goals, constraints, or context
        (for example, using phrasing like "how to ..." or "best ... for ...").
        Generate search queries that are clearly scoped and purposeful, with enough detail
        to signal intent and context.
    """
    ,
}


def get_prompt(profile: dict) -> str:
    """Return the specificity prompt, using age_group + prior_task_knowledge."""
    age = profile.get("age_group", "younger")
    prior = profile.get("prior_task_knowledge")

    if age == "younger" and prior in (None, "medium", "high"):
        level = "specific"
    elif age == "older" and prior == "high":
        level = "specific"
    elif prior == "low":
        level = "vague"
    else:
        level = "moderate"

    return PROMPTS[level]

