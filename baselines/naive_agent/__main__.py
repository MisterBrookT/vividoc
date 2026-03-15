"""CLI entry point: python -m baselines.naive_agent <topic> <model>"""

import argparse
from .runner import NaiveAgentRunner


def main():
    parser = argparse.ArgumentParser(description="Naive Agent baseline")
    parser.add_argument("topic", help="Topic for the document")
    parser.add_argument(
        "model",
        nargs="?",
        default="openrouter/google/gemini-3-flash-preview",
        help="LLM model (default: openrouter/google/gemini-3-flash-preview)",
    )
    parser.add_argument("--output-dir", default="outputs", help="Output directory")
    args = parser.parse_args()

    runner = NaiveAgentRunner(llm_model=args.model, output_dir=args.output_dir)
    result = runner.run(args.topic)
    print(result)


if __name__ == "__main__":
    main()
