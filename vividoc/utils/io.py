import json
import re
def extract_from_markdown(text: str) -> dict | str:
    """
    Extract content from LLM response with fenced code block.
    If no code block found, return original text.
    """
    # Match any fenced code block: ```lang or just ```
    pattern = r"```(?:\w+)?\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)

    if match:
        content = match.group(1).strip()
        # Try JSON first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content

    # No code block, return original text

    return text