"""Simple CLI pipeline for vividoc."""

import typer
from vividoc.core import (
    Planner,
    Executor,
    Evaluator,
    Runner,
    RunnerConfig,
    DocumentSpec,
    GeneratedDocument,
)
from vividoc.utils.io import save_json, load_json

# Create main app
app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
):
    """Start the web server for ViviDoc UI."""
    import uvicorn
    from vividoc.entrypoint import create_app

    typer.echo(f"🚀 Starting ViviDoc web server on {host}:{port}")
    if reload:
        typer.echo("🔄 Auto-reload enabled")

    app_instance = create_app()
    uvicorn.run(app_instance, host=host, port=port, reload=reload)


@app.command()
def plan(
    topic: str = typer.Argument(..., help="Topic for the document"),
    llm_model: str = typer.Argument(
        ..., help="LLM model in format provider/model-name"
    ),
    output: str = typer.Option("output/doc_spec.json", help="Output file path"),
):
    """Execute planning phase - Generate document specification."""
    typer.echo(f"🎯 Planning document for topic: {topic}")
    typer.echo(f"🤖 Using model: {llm_model}")

    config = RunnerConfig(llm_model=llm_model)
    planner = Planner(config=config)

    doc_spec = planner.run(topic)
    save_json(doc_spec, output)

    typer.echo(f"✅ Generated {len(doc_spec.knowledge_units)} knowledge units")
    typer.echo(f"📄 Saved to: {output}")


@app.command()
def exec(
    spec_file: str = typer.Argument(..., help="Path to document spec JSON file"),
    llm_model: str = typer.Argument(
        ..., help="LLM model in format provider/model-name"
    ),
    output: str = typer.Option("output/generated_doc.json", help="Output file path"),
):
    """Execute execution phase - Generate text and code."""
    typer.echo(f"🚀 Executing document generation from: {spec_file}")
    typer.echo(f"🤖 Using model: {llm_model}")

    # Load spec
    doc_spec = load_json(spec_file, DocumentSpec)

    config = RunnerConfig(llm_model=llm_model, output_dir="output")
    executor = Executor(config=config)

    generated_doc = executor.run(doc_spec)
    save_json(generated_doc, output)

    typer.echo(f"✅ Generated {len(generated_doc.knowledge_units)} knowledge units")
    typer.echo(f"📄 Saved to: {output}")


@app.command()
def eval(
    doc_file: str = typer.Argument(..., help="Path to generated document JSON file"),
    llm_model: str = typer.Argument(
        ..., help="LLM model in format provider/model-name"
    ),
    output: str = typer.Option("output/evaluation.json", help="Output file path"),
):
    """Execute evaluation phase - Validate document quality."""
    typer.echo(f"📊 Evaluating document from: {doc_file}")
    typer.echo(f"🤖 Using model: {llm_model}")

    # Load document
    generated_doc = load_json(doc_file, GeneratedDocument)

    config = RunnerConfig(llm_model=llm_model)
    evaluator = Evaluator(config=config)

    feedback = evaluator.run(generated_doc)
    save_json(feedback, output)

    if feedback.requires_revision:
        typer.echo(
            f"⚠️  Document requires revision: {len(feedback.component_issues)} issues"
        )
    else:
        typer.echo("✅ Document validated successfully")

    typer.echo(f"📄 Saved to: {output}")


@app.command()
def run(
    topic: str = typer.Argument(..., help="Topic for the document"),
    llm_model: str = typer.Argument(
        ..., help="LLM model in format provider/model-name"
    ),
    output_dir: str = typer.Option("outputs", help="Output directory"),
    resume: bool = typer.Option(
        False, "--resume", help="Resume from existing files if available"
    ),
):
    """Run complete pipeline: plan → exec → eval."""
    typer.echo(f"🔄 Running complete pipeline for topic: {topic}")
    typer.echo(f"🤖 Using model: {llm_model}")
    if resume:
        typer.echo("📂 Resume mode: will skip existing files")

    config = RunnerConfig(output_dir=output_dir, resume=resume, llm_model=llm_model)
    runner = Runner(config=config)

    _ = runner.run(topic)

    typer.echo("✅ Pipeline completed!")
    typer.echo(f"📁 Output directory: {output_dir}")


def main():
    """Entry point for the vividoc CLI."""
    app()


if __name__ == "__main__":
    main()
