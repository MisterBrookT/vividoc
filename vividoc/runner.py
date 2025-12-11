"""Runner workflow for vividoc pipeline."""

from dataclasses import dataclass
from typing import Optional

from .planner import Planner
from .executor import Executor
from .evaluator import Evaluator


@dataclass
class RunnerConfig:
    """Configuration for running complete pipeline."""
    # TODO: Add pipeline-level parameters
    pass


class Runner:
    """Handles the complete pipeline execution."""
    
    def __init__(self, config: RunnerConfig):
        """Initialize runner with configuration."""
        self.config = config
    
    def run(self) -> bool:
        """Execute the complete pipeline: plan → exec → eval."""
        # Phase 1: Planning
        raise NotImplementedError("Not implemented")