def prompt_website_category(url: str) -> str:
    return f"""
You are an expert at classifying technical and interactive educational websites.

Given a webpage, analyze it and extract a concise three-part classification describing:
1. Accessibility — Whether the webpage is currently reachable and loads successfully.
2. IsExplorable — Whether the webpage is an "Explorable Explanation" or contains key features such as interactive diagrams, simulations, reactive visualizations, or dynamic explanations.

URL:
{url}

Requirement:
- Return **only** the JSON object with no additional commentary.
- Ensure all sentences are fully self-contained.
- For "accessible", return true or false.
- For "is_explorable", return true or false.
- For "category", return exactly one short label.

Output Format:
```json
{{
    "accessible": true,
    "is_explorable": true,
}}
```
"""
