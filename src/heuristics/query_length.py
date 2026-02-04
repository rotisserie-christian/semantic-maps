# younger user = longer queries
# older user = shorter queries

PROMPTS = {
    "younger": 
    """
        This user tends to use longer search queries, often with more words or full questions. 
        Generate search queries that reflect that: typically longer phrases (ex. 5+ words), 
        including complete questions or descriptive phrases where natural.
    """
    ,
    "older": 
    """
        This user tends to use shorter, more concise search queries with fewer words. 
        Generate search queries that reflect that: typically 2-4 words, keyword-style, 
        without long descriptive phrases or full sentences.
    """
    ,
}


def get_prompt(profile: dict) -> str:
    """Returns query_length prompt, uses age_group only."""
    age = profile.get("age_group", "younger")
    return PROMPTS.get(age, PROMPTS["younger"])
