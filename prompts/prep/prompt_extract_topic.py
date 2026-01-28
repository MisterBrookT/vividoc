def prompt_topic_extraction(url: str) -> str:
    return f"""
You are an expert in summarizing Explorable Explanations.

Given an interactive explorable webpage, extract a concise two-part summary::
1. Topic — A highly abstract, minimal conceptual description.
   - Do NOT describe the visualization, the page, how it teaches, or what is shown.
   - Do NOT include actions, UI elements, animations, or phrasing such as "this explorable", "visually shows", "demonstrates", "allows users", etc.
   - Write the topic like a textbook chapter title or concept label.
   - Examples of acceptable topic styles:
       • "How Conditional probability works"
       • "Markov chains and state transitions"
       • "Eigenvectors under linear transformations"
       • "Fourier decomposition of signals"
       ...
2. Interaction Forms — A compact list describing all the types of interactions and how the visualization responds when users manipulate them.


URL:
{url}

Requirement:
- The summary must contain only the two parts above.
- Do not omit any interaction.
- For each interaction form, output a label, followed by one fully self-contained sentence that elaborates on it. 
- Return **only** the JSON object with no additional commentary.

Output Format:
```json
{{
    "topic": "A short, abstract concept phrase.",
    "interaction_forms": [
        {{
            "label": "Interaction Form 1",
            "description": "A fully self-contained sentence that elaborates on the interaction form."
        }},
        {{
            "label": "Interaction Form 2",
            "description": "A fully self-contained sentence that elaborates on the interaction form."
        }},
        ...
    ]
}}
```
"""
