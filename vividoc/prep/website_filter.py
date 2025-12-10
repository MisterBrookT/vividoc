import csv
import os
from tqdm import tqdm

from prompts.prep.promtp_website_category import prompt_website_category
from google import genai
from google.genai.types import GenerateContentConfig
from vividoc.utils.io import extract_from_markdown
from vividoc.utils.logger import logger
client = genai.Client()

INPUT_CSV = "datasets/raw/raw.csv"
OUTPUT_CSV = "datasets/prepped/prepped.csv"

tools = [
  {"url_context": {}},
]
def classify_url(url: str) -> str:
    prompt = prompt_website_category(url)
    return client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config = GenerateContentConfig(
            tools=tools,
        )
    ).text

def main():
    rows = []

    # read CSV
    with open(INPUT_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    # check if output file exists and read already processed URLs
    processed_urls = set()
    file_exists = os.path.exists(OUTPUT_CSV)
    
    if file_exists:
        with open(OUTPUT_CSV, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed_urls.add(row["link"])
        print(f"Found {len(processed_urls)} already processed URLs. Resuming...")
    
    # filter out already processed rows
    rows_to_process = [r for r in rows if r["link"] not in processed_urls]
    
    if not rows_to_process:
        print("All URLs already processed!")
        return
    
    print(f"Processing {len(rows_to_process)} remaining URLs out of {len(rows)} total")

    # if file doesn't exist, create it with header
    if not file_exists:
        with open(OUTPUT_CSV, "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=[
                    "field", "link", "accessible",
                    "is_explorable"
                ]
            )
            writer.writeheader()

    # classify each link and write immediately
    for r in tqdm(rows_to_process, desc="Classifying URLs"):
        url = r["link"]

        try:
            result = classify_url(url)
            result = extract_from_markdown(result)
        except Exception as e:
            logger.error(f"Error for {url}: {e}")
            continue

        output_row = {
            "field": r["field"],
            "link": url,
            "accessible": result["accessible"],
            "is_explorable": result["is_explorable"],
        }
        
        # append to file immediately
        with open(OUTPUT_CSV, "a", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=[
                    "field", "link", "accessible",
                    "is_explorable"
                ]
            )
            writer.writerow(output_row)

    print(f"\nDone! Saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()