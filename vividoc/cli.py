"""Simple CLI pipeline for vividoc."""

import typer
from typing import Optional

from .planner import Planner, PlannerConfig
from .executor import Executor, ExecutorConfig
from .evaluator import Evaluator, EvaluatorConfig
from .runner import Runner, RunnerConfig

# Create main app
app = typer.Typer(no_args_is_help=True)



@app.command()
def plan(
    arg1: Optional[str] = typer.Argument(None, help="First argument"),
    arg2: Optional[str] = typer.Argument(None, help="Second argument")
):
    """
    Execute planning phase - Stage 1
    """
    cfg = PlannerConfig()
    typer.echo("🎯 Plan Phase: Creating execution plan")
    
    planner = Planner(config=cfg)
    planner.run()


@app.command()
def exec(
    arg1: Optional[str] = typer.Argument(None, help="First argument"),
    arg2: Optional[str] = typer.Argument(None, help="Second argument")
):
    """
    Execute plan - Stage 2
    """
    cfg = ExecutorConfig()
    typer.echo("🚀 Exec Phase: Executing plan")
    
    executor = Executor(config=cfg)
    executor.run()


@app.command()
def eval(
    arg1: Optional[str] = typer.Argument(None, help="First argument"),
    arg2: Optional[str] = typer.Argument(None, help="Second argument")
):
    """
    Evaluate execution results - Stage 3
    """
    cfg = EvaluatorConfig()
    typer.echo("📊 Eval Phase: Evaluating execution results")
    
    evaluator = Evaluator(config=cfg)
    evaluator.run()


@app.command()
def run(
    arg1: Optional[str] = typer.Argument(None, help="First argument"),
    arg2: Optional[str] = typer.Argument(None, help="Second argument")
):
    """
    Run complete pipeline: plan → exec → eval
    """
    cfg = RunnerConfig()
    typer.echo("🔄 Running complete pipeline...")
    
    runner = Runner(config=cfg)
    runner.run()


def main():
    """Entry point for the vividoc CLI."""
    app()


if __name__ == "__main__":
    main()
