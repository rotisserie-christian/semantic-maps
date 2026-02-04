# novice user = sticks to initial terms
# expert user = strategic reformulation with new keywords

PROMPTS = {
    "sticks":
    """
        This user tends to stick with the same strategy from their initial search terms.
        They are less likely to reframe the query strategically.
        Generate search queries that reuse the same core terms and make only small variations,
        such as changing word order or adding a very limited number of simple modifiers.
    """
    ,
    "moderate":
    """
        This user sometimes reformulates their queries when results are not ideal,
        but does so in a relatively incremental way.
        Generate search queries that reuse some core terms while introducing a few new keywords
        or slight reframings to explore alternatives, without radically changing the query.
    """
    ,
    "strategic":
    """
        This user is more strategic about reformulating queries when results are not ideal.
        They are comfortable introducing new, related keywords and reframing the query
        to probe different aspects of the topic.
        Generate search queries that show this behaviour: reuse important core terms,
        but also add or substitute new, related keywords to explore alternative angles.
    """
    ,
}


def get_prompt(profile: dict) -> str:
    """Return the reformulation prompt, using domain_expertise and age_group (optional)"""
    expertise = profile.get("domain_expertise", "novice")

    if expertise == "novice":
        level = "sticks"
    elif expertise == "expert":
        level = "strategic"
    else:
        level = "moderate"

    return PROMPTS[level]

