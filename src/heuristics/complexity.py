# older novice user = simpler initial queries
# younger expert user = more elaborate initial queries

PROMPTS = {
    "simple": 
    """
        This user tends to start with simple, less elaborate search queries,
        often using only a few core keywords and minimal detail.
        Generate initial search queries that are straightforward and relatively short,
        without many qualifiers or sub-clauses.
    """
    ,
    "moderate": 
    """
        This user tends to start with moderately elaborate search queries,
        using several keywords and some descriptive detail.
        Generate initial search queries that balance brevity with clarity:
        include a few key descriptors, but avoid overly long, complex sentences.
    """
    ,
    "elaborate": 
    """
        This user tends to start with more elaborate search queries,
        combining multiple keywords and detailed phrasing.
        Generate initial search queries that are richer in detail,
        longer phrases that specify context, goals, and constraints.
    """
    ,
}


def get_prompt(profile: dict) -> str:
    """Return the complexity prompt, uses age_group + domain_expertise"""
    age = profile.get("age_group", "younger")
    expertise = profile.get("domain_expertise", "novice")

    if age == "older" and expertise == "novice":
        level = "simple"
    elif age == "younger" and expertise == "expert":
        level = "elaborate"
    else:
        level = "moderate"

    return PROMPTS[level]

