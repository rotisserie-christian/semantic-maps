profile = {
    # younger/older: drives query length, complexity, specificity, word choice
    "age_group": "older",

    # novice/intermediate/expert: domain expertise for the search topic
    "domain_expertise": "novice",

    # Free text description of the user: goals, constraints, background, etc.
    "description": "",

    # (Optional) low/medium/high: prior task/topic knowledge (reduces age effects)
    "prior_task_knowledge": None,

    # (Optional) low/medium/high: general web/search experience
    "internet_experience": None,
}

replicate = {
    "env": "REPLICATE_API_TOKEN",
    "model": "google/gemini-3.1-pro", # Model identifier
    "max_tokens": 150048,
    "temperature": 1.0,
}
