"""Terminal test script for chat streaming endpoint.

Usage:
    python test_chat_stream.py <spec_id> "<message>"

Example:
    python test_chat_stream.py c77a09b3-fde2-0933-a56a-d76c03c3ea16 "把标题改成红色"
"""

import sys
import json
import requests

BASE_URL = "http://localhost:8000"


def main():
    if len(sys.argv) < 3:
        print('Usage: python test_chat_stream.py <spec_id> "<message>"')
        sys.exit(1)

    spec_id = sys.argv[1]
    message = sys.argv[2]

    print("=== Chat Stream Test ===")
    print(f"Spec ID: {spec_id}")
    print(f"Message: {message}")
    print("========================\n")

    resp = requests.post(
        f"{BASE_URL}/api/chat",
        json={"spec_id": spec_id, "message": message},
        stream=True,
        timeout=120,
    )

    if resp.status_code != 200:
        print(f"ERROR: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    full_text = ""
    token_count = 0

    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        try:
            event = json.loads(line[6:])
        except json.JSONDecodeError:
            continue

        if event["type"] == "token":
            token = event["content"]
            full_text += token
            token_count += 1
            sys.stdout.write(token)
            sys.stdout.flush()
        elif event["type"] == "edit_mode_start":
            print("\n\n>>> [EDIT_MODE detected] <<<\n")
        elif event["type"] == "html_updated":
            html_len = len(event.get("html", ""))
            print(f"\n\n>>> [HTML UPDATED - {html_len} chars] <<<")
        elif event["type"] == "done":
            print(
                f"\n\n>>> [DONE] Total tokens: {token_count}, Total chars: {len(full_text)} <<<"
            )
        elif event["type"] == "error":
            print(f"\n\n>>> [ERROR] {event.get('content', 'unknown')} <<<")

    print("\n\n=== Full Response Stats ===")
    print(f"Total tokens: {token_count}")
    print(f"Total chars: {len(full_text)}")
    has_edit_mode = "[EDIT_MODE]" in full_text
    print(f"Contains [EDIT_MODE]: {has_edit_mode}")
    edit_block_count = full_text.count("```edit")
    print(f"Edit blocks found: {edit_block_count}")


if __name__ == "__main__":
    main()
