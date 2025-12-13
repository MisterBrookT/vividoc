"""Planner workflow for vividoc pipeline."""

import argparse
import json
import os
from typing import List
from dataclasses import dataclass
import google.generativeai as genai
from prompt_planner import prompt_planner

os.environ["http_proxy"] = "http://127.0.0.1:54465"
os.environ["https_proxy"] = "http://127.0.0.1:54465"

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
    api_key: str
    model_name: str

class Planner:
    """Handles the planning phase of the vividoc pipeline."""
    
    def __init__(self, config: PlannerConfig):
        """Initialize planner with configuration."""
        self.config = config

        genai.configure(api_key=self.config.api_key)

        self.model = genai.GenerativeModel(
            model_name = self.config.model_name
        )
    
    def run(self,topic: str) -> TeachingPlan:
        """Execute the planning phase."""
        prompt_content=prompt_planner(topic)
        response=self.model.generate_content(
            prompt_content,
            generation_config = {"response_mime_type": "application/json"}
        )
        print(response.text)

        os.makedirs("output",exist_ok=True)
        safe_topic = topic.replace(" ","_")
        for char in ['?',':','/','\\','*','"','<','>','|']:
            safe_topic = safe_topic.replace(char,"")
        filename = safe_topic+".json"
        file_path = os.path.join("output",filename)
        with open(file_path,"w",encoding = "utf-8") as f:
            f.write(response.text)
        
        raw_data=json.loads(response.text)
        units=[]
        for item in raw_data.get("knowledge_units",[]):
            unit = KnowledgeUnit(
                id = item.get("id"),
                unit_content = item.get("unit_content"),
                text_description=item.get("text_description"),
                interaction_description = item.get("interaction_description")
            )
            units.append(unit)
        plan = TeachingPlan(
            topic=raw_data.get("topic",topic),
            knowledge_units=units
        )
        return plan

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description = "Run Planner Agent")
    parser.add_argument("--topic",type = str,help = "Please enter teaching topic")
    parser.add_argument("--api_key",type = str,help = "Please enter your API Key")
    args = parser.parse_args()

    cfg = PlannerConfig(
        api_key = args.api_key,
        model_name = "gemini-2.5-pro"
    )
    agent=Planner(cfg)

    result=agent.run(args.topic)

    if result:
        print(f"\nOutline Preview: {result.topic}")
        for u in result.knowledge_units:
            print(f"- {u.id}\n{u.unit_content}")