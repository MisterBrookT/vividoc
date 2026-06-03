"""HTML template generator — structural skeleton only, no opinionated styles."""

from vividoc.core.models import DocumentSpec


def create_document_skeleton(doc_spec: DocumentSpec, output_path: str) -> None:
    """Create an HTML document skeleton with empty sections and no preset styles.

    The <style> block is intentionally minimal — callers (the /vividoc skill or
    the Executor with style instructions) are expected to replace it entirely with
    a custom design derived from the topic's character.
    """
    sections = []
    for idx, ku in enumerate(doc_spec.knowledge_units, 1):
        scope_id = f"ku{idx}"
        section_html = f"""    <section class="knowledge-unit" id="{scope_id}">
        <h2 class="ku-title">{ku.unit_content}</h2>
        <div class="text-content">
            <!-- Stage 1: text content -->
        </div>
        <div class="interactive-content">
            <!-- Stage 2: interactive visualization -->
        </div>
    </section>"""
        sections.append(section_html)

    sections_html = "\n\n".join(sections)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{doc_spec.topic}</title>

    <!-- KaTeX -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>

    <!-- D3 + Chart.js -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

    <style>
        /* CUSTOM STYLES — replace this entire block with topic-specific design */
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: sans-serif; line-height: 1.6; padding: 40px; }}
        .knowledge-unit {{ margin-bottom: 40px; }}
        .text-content {{ margin-bottom: 20px; }}
        .text-content p {{ margin-bottom: 1em; }}
        .interactive-content {{ margin-top: 16px; }}
    </style>
</head>
<body>
    <h1>{doc_spec.topic}</h1>

{sections_html}

    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{left: "$$", right: "$$", display: true}},
                    {{left: "$", right: "$", display: false}}
                ],
                throwOnError: false
            }});
        }});
    </script>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
