"""Planner workflow for vividoc pipeline."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from prompts.prompt_planner import build_planner_prompt
from vividoc.utils.io import extract_from_markdown
from vividoc.utils.llm.client import LLMClient

@dataclass
class KnowledgeUnit:
    id: str
    unit_content: str
    text_description: str
    interaction_description: str

@dataclass
class TeachingPlan:
    topic: str
    knowledge_units: List[KnowledgeUnit]

@dataclass
class PlannerConfig:
    """Configuration for planning phase."""
    topic: str|None = None
    model_name: str = "gemini-2.5-pro"
    output_dir: Path = Path("outputs")
    llm_provider: Optional[str] = None

class Planner:
    """Handles the planning phase of the vividoc pipeline."""
    
    def __init__(self, config: PlannerConfig):
        """Initialize planner with configuration."""
        self.config = config
        provider = self.config.llm_provider or "google"
        self.client = LLMClient(provider)
    
    def run(self) -> TeachingPlan:
        """Execute the planning phase."""
        topic = self.config.topic
        if not topic: 
            raise ValueError(
                "PlannerConfig.topic is not set. "
                "CLI must provide topic via configuration."
            )
        prompt = build_planner_prompt(topic)
        llm_response = self.client.call_text_generation(
            model=self.config.model_name,
            prompt=prompt,
        )

        if not isinstance(llm_response, str):
            raw_data = llm_response
        else:
            normalized = extract_from_markdown(llm_response)
            raw_data = normalized if isinstance(normalized, dict) else json.loads(normalized)
        units: List[KnowledgeUnit] = []
        for item in raw_data.get("knowledge_units",[]):
            unit = KnowledgeUnit(
                id = item.get("id",""),
                unit_content = item.get("unit_content",""),
                text_description=item.get("text_description",""),
                interaction_description = item.get("interaction_description","")
            )
            units.append(unit)
        plan = TeachingPlan(
            topic=raw_data.get("topic",topic),
            knowledge_units=units
        )

        self.config.output_dir.mkdir(parents = True,exist_ok = True)

        safe_topic = "".join(
            c for c in topic.replace(" ","_")
            if c.isalnum() or c in ("_","-")
        )
        output_path = self.config.output_dir/f"{safe_topic}.json"

        with open(output_path,"w",encoding = "utf-8") as f:
            json.dump(raw_data,f,ensure_ascii = False,indent=2)
        
        return plan