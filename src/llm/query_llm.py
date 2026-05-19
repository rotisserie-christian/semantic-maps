from typing import Dict, List, Optional
import os
import replicate
from src.config import replicate as replicate_config
from src.llm.assemble_prompts import build_prompt


def _call_replicate(prompt: str) -> str:
    """
    Call the Replicate model configured in src.config with the given prompt

    Returns the full text output from the model
    """
    # Ensure the expected API token is present for clearer errors
    env_var = replicate_config.get("env", "REPLICATE_API_TOKEN")
    if not os.getenv(env_var):
        raise RuntimeError(
            f"{env_var} environment variable is missing"
        )

    model = replicate_config["model"]
    max_tokens = replicate_config.get("max_tokens", 2048)
    temperature = replicate_config.get("temperature", 1.0)

    output = replicate.run(
        model,
        input={
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
    )

    # Replicate may stream tokens (list/iterator) or return a single string.
    if isinstance(output, str):
        return output

    # Safely join any iterable of chunks into one string.
    return "".join(str(chunk) for chunk in output)


def query_llm(
    profile_override: Optional[Dict[str, object]] = None,
    prompt_override: Optional[str] = None,
    return_raw: bool = False
) -> str | List[str]:
    """
    Build a prompt for the given (or default) profile and query the LLM.

    Args:
        profile_override: Dictionary to override the user profile.
        prompt_override: Direct string to use as the prompt (bypasses build_prompt).
        return_raw: If True, returns the full string output instead of a list of lines.

    Returns:
        The full model output string or a list of lines.
    """
    if prompt_override:
        prompt = prompt_override
    else:
        prompt = build_prompt(profile_override)
        
    raw_text = _call_replicate(prompt)

    if return_raw:
        return raw_text

    queries: List[str] = []
    for line in raw_text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        # Strip off numbering
        if cleaned[:2].isdigit() and len(cleaned) > 2:
            rest = cleaned[2:].lstrip(".). \t")
            if rest:
                cleaned = rest
        queries.append(cleaned)

    return queries


if __name__ == "__main__":
    for q in query_llm():
        print(q)

