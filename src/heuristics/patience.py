# older user = more time per SERP, more evaluation
# younger user = quicker to adjust or move on

PROMPTS = {
    "quick":
    """
        This user tends to move quickly through search results and is more likely
        to adjust or replace their query rather than spending a long time reading
        each result.
        Generate search queries that reflect this behaviour: assume they will try
        several different queries rather than deeply evaluating long result pages.
    """
    ,
    "moderate":
    """
        This user balances evaluating results and adjusting queries.
        They will read some results in detail but will also reformulate when needed.
        Generate search queries that are suitable for a mix of brief scanning and
        occasional deeper reading of results.
    """
    ,
    "thorough":
    """
        This user tends to spend more time on each results page, carefully
        evaluating what they see before changing their query.
        Generate search queries that support this behaviour: assume they will
        scroll and read more, so queries can be slightly broader to invite
        evaluation of multiple results on each page.
    """
    ,
}


def get_prompt(profile: dict) -> str:
    """Return the patience prompt, using age_group"""
    age = profile.get("age_group", "younger")

    if age == "younger":
        level = "quick"
    elif age == "older":
        level = "thorough"
    else:
        level = "moderate"

    return PROMPTS[level]

