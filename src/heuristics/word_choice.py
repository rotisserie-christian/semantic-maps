# younger user = more confident/casual phrasing ("best", "how to")
# expert user = more jargon and domain-specific terms

PROMPTS = {
    "simple":
    """
        This user tends to use simpler, more generic wording in their searches.
        They favour everyday language over technical jargon.
        Generate search queries that use clear, accessible vocabulary rather than
        specialised or highly technical terms.
    """
    ,
    "confident":
    """
        This user tends to use more confident phrasing in their searches,
        including words like "best", "how to", or "top" when appropriate.
        Generate search queries that sound purposeful and assured, while still
        using mostly everyday language.
    """
    ,
    "expert":
    """
        This user tends to use more specialised, domain-specific vocabulary.
        They are comfortable with technical terms and jargon relevant to the topic.
        Generate search queries that incorporate appropriate technical or expert
        terminology, while still remaining natural for a search engine query.
    """
    ,
}


def get_prompt(profile: dict) -> str:
    """Return the word_choice prompt, using age_group + domain_expertise."""
    age = profile.get("age_group", "younger")
    expertise = profile.get("domain_expertise", "novice")

    if expertise == "expert":
        level = "expert"
    elif age == "younger":
        level = "confident"
    else:
        level = "simple"

    return PROMPTS[level]

