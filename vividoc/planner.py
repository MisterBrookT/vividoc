"""Planner workflow for vividoc pipeline."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

import google.generativeai as genai
from prompts.prompt_planner import build_planner_prompt

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

class Planner:
    """Handles the planning phase of the vividoc pipeline."""
    
    def __init__(self, config: PlannerConfig):
        """Initialize planner with configuration."""
        self.config = config

        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY is not set. "
                "Please export it as an environment variable."
            )
        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            model_name = self.config.model_name
        )
    
    def run(self) -> TeachingPlan:
        """Execute the planning phase."""
        topic = self.config.topic
        if not topic: 
            raise ValueError(
                "PlannerConfig.topic is not set. "
                "CLI must provide topic via configuration."
            )
        prompt=build_planner_prompt(topic)
        response=self.model.generate_content(
            prompt,
            generation_config = {"response_mime_type": "application/json"}
        )
        text = response.text
        
        try:
            raw_data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse LLM response as JSON: {e}\n"
                f"Response was:\n{text}"
            )
        
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