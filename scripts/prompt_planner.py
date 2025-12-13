def prompt_planner(topic: str) -> str:
    return f"""
You are a professional interactive educational document designer.
Please design a teaching outline of the topic "{topic}".

Please strictly follow the JSON structure below:
{{
    "topic": "{topic}",
    "knowledge_units": [
        {{
            "id": "ku1",
            "unit_content": "summary of the core knowledge points",
            "text_description": "detailed teaching text content",
            "interaction_description": "description of interactive component"
        }}
        ...
    ]"
}}
"""