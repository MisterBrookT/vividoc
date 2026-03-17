"""Functional evaluation using Playwright.

Two sub-scores combined into one Functional Correctness score:
1. Render Correctness: page loads, no JS errors, DOM has content
2. Interaction Functionality: interactive elements respond to events

Also captures a screenshot for Visual Quality evaluation.
"""

from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


def _collect_interactive_elements(page) -> list[dict]:
    """Find all interactive elements in the page."""
    elements = []
    # Buttons
    for btn in page.query_selector_all("button"):
        elements.append({"type": "button", "el": btn})
    # Range sliders
    for slider in page.query_selector_all("input[type=range]"):
        elements.append({"type": "slider", "el": slider})
    # Clickable inputs (checkbox, radio)
    for inp in page.query_selector_all("input[type=checkbox], input[type=radio]"):
        elements.append({"type": "toggle", "el": inp})
    # Select dropdowns
    for sel in page.query_selector_all("select"):
        elements.append({"type": "select", "el": sel})
    # Elements with onclick attribute
    for el in page.query_selector_all("[onclick]"):
        if el not in [e["el"] for e in elements]:
            elements.append({"type": "onclick", "el": el})
    return elements


def _get_dom_snapshot(page) -> str:
    """Get a lightweight DOM snapshot for change detection."""
    return page.evaluate("() => document.body.innerHTML.length.toString()")


def evaluate_functional(html_path: str, screenshot_dir: str | None = None) -> dict:
    """Evaluate render correctness and interaction functionality.

    Args:
        html_path: Path to the HTML file
        screenshot_dir: If provided, save a full-page screenshot here

    Returns:
        dict with render_correctness and interaction_functionality scores (0-1)
        plus detailed breakdown.
    """
    html_path = Path(html_path)
    if not html_path.exists():
        return {
            "render_correctness": 0.0,
            "interaction_functionality": 0.0,
            "error": "HTML file not found",
        }

    file_url = f"file://{html_path.resolve()}"
    result = {
        "js_errors": [],
        "console_warnings": [],
        "dom_element_count": 0,
        "has_content": False,
        "interactive_elements_found": 0,
        "interactive_elements_responsive": 0,
        "interaction_details": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        # Collect console errors
        js_errors = []
        page.on(
            "console",
            lambda msg: (js_errors.append(msg.text) if msg.type == "error" else None),
        )
        page.on("pageerror", lambda err: js_errors.append(str(err)))

        # Load page
        try:
            page.goto(file_url, wait_until="networkidle", timeout=15000)
        except PWTimeout:
            page.goto(file_url, wait_until="domcontentloaded", timeout=10000)

        # Wait a bit for JS to execute
        page.wait_for_timeout(1000)

        result["js_errors"] = js_errors[:20]  # cap

        # DOM analysis
        body_text = page.evaluate("() => document.body?.innerText?.length || 0")
        dom_count = page.evaluate("() => document.querySelectorAll('*').length")
        result["dom_element_count"] = dom_count
        result["has_content"] = body_text > 50

        # Screenshot
        if screenshot_dir:
            ss_dir = Path(screenshot_dir)
            ss_dir.mkdir(parents=True, exist_ok=True)
            ss_path = ss_dir / "screenshot.png"
            page.screenshot(path=str(ss_path), full_page=True)
            result["screenshot_path"] = str(ss_path)

        # --- Interaction Functionality ---
        interactive = _collect_interactive_elements(page)
        result["interactive_elements_found"] = len(interactive)

        responsive_count = 0
        for item in interactive:
            el = item["el"]
            el_type = item["type"]
            detail = {"type": el_type, "responded": False}

            try:
                # Snapshot before interaction
                before = page.evaluate("() => document.body.innerHTML")

                if el_type == "slider":
                    # Move slider to a different value
                    cur = el.evaluate("e => e.value")
                    max_val = el.evaluate("e => e.max || '100'")
                    min_val = el.evaluate("e => e.min || '0'")
                    fmax = float(max_val)
                    fmin = float(min_val)
                    mid = (fmax + fmin) / 2
                    third = fmin + (fmax - fmin) / 3
                    new_val = mid if str(cur) != str(mid) else third
                    el.evaluate(
                        f"e => {{ e.value = {new_val}; e.dispatchEvent(new Event('input', {{bubbles:true}})); e.dispatchEvent(new Event('change', {{bubbles:true}})); }}"
                    )
                elif el_type == "select":
                    options = el.evaluate(
                        "e => Array.from(e.options).map(o => o.value)"
                    )
                    if len(options) > 1:
                        el.select_option(index=1)
                elif el_type in ("button", "onclick"):
                    el.click(timeout=2000)
                elif el_type == "toggle":
                    el.click(timeout=2000)

                page.wait_for_timeout(500)

                # Snapshot after interaction
                after = page.evaluate("() => document.body.innerHTML")

                if before != after:
                    detail["responded"] = True
                    responsive_count += 1

            except Exception as e:
                detail["error"] = str(e)[:100]

            result["interaction_details"].append(detail)

        result["interactive_elements_responsive"] = responsive_count

        browser.close()

    # --- Compute scores ---
    # Render Correctness: 0-1
    render_score = 1.0
    if not result["has_content"]:
        render_score -= 0.5
    if result["js_errors"]:
        # Deduct based on number of errors (max 0.5 deduction)
        render_score -= min(0.5, len(result["js_errors"]) * 0.1)
    render_score = max(0.0, render_score)

    # Interaction Functionality: 0-1
    n_found = result["interactive_elements_found"]
    n_responsive = result["interactive_elements_responsive"]
    if n_found == 0:
        interaction_score = 0.0  # no interactive elements at all
    else:
        interaction_score = n_responsive / n_found

    result["render_correctness"] = round(render_score, 2)
    result["interaction_functionality"] = round(interaction_score, 2)

    return result
