import csv
import json
import os
from tqdm import tqdm

from google import genai
from google.genai.types import GenerateContentConfig
from prompts.prep.prompt_extract_topic import prompt_topic_extraction
from vividoc.utils.io import extract_from_markdown

INPUT_CSV = "datasets/prepped/explorable.csv"
OUTPUT_JSONL = "datasets/prepped/topics.jsonl"

client = genai.Client()
tools = [
    {"url_context": {}},
]


def extract_topic(url: str) -> dict:
    """Extract topic and interaction forms from a URL."""
    result = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt_topic_extraction(url),
        config=GenerateContentConfig(
            tools=tools,
        ),
    ).text
    return extract_from_markdown(result)


def main():
    rows = []

    # read CSV
    with open(INPUT_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["link"]:  # skip empty rows
                rows.append(r)

    # check if output file exists and read already processed URLs
    processed_urls = set()
    file_exists = os.path.exists(OUTPUT_JSONL)

    if file_exists:
        with open(OUTPUT_JSONL, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    processed_urls.add(data["url"])
        print(f"Found {len(processed_urls)} already processed URLs. Resuming...")

    # filter out already processed rows
    rows_to_process = [r for r in rows if r["link"] not in processed_urls]

    if not rows_to_process:
        print("All URLs already processed!")
        return

    print(f"Processing {len(rows_to_process)} remaining URLs out of {len(rows)} total")

    # extract topics for each link and write immediately
    for r in tqdm(rows_to_process, desc="Extracting topics"):
        url = r["link"]

        try:
            result = extract_topic(url)

            # create output record
            output_record = {
                "field": r.get("field", ""),
                "url": url,
                "topic": result.get("topic", ""),
                "interaction_forms": result.get("interaction_forms", []),
            }

            # append to JSONL file immediately
            with open(OUTPUT_JSONL, "a") as f:
                f.write(json.dumps(output_record, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"\nError for {url}: {e}")
            # Write error record
            continue

    print(f"\nDone! Saved to {OUTPUT_JSONL}")


if __name__ == "__main__":
    main()
