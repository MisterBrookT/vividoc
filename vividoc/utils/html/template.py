"""HTML template generator for iterative document creation."""

from vividoc.core.models import DocumentSpec


def create_document_skeleton(doc_spec: DocumentSpec, output_path: str) -> None:
    """Create initial HTML document skeleton with empty sections.

    Args:
        doc_spec: Document specification with knowledge units
        output_path: Path to save the HTML skeleton
    """

    # Generate section skeletons
    sections = []
    for idx, ku in enumerate(doc_spec.knowledge_units, 1):
        scope_id = f"ku{idx}"
        section_html = f'''    <!-- {ku.unit_content} -->
    <section class="knowledge-unit" id="{scope_id}">
        <div class="text-content">
            <!-- Stage 1: Text content will be filled here -->
        </div>
        <div class="interactive-content">
            <!-- Stage 2: Interactive content will be filled here -->
        </div>
    </section>'''
        sections.append(section_html)

    sections_html = "\n\n".join(sections)

    # Complete HTML template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{doc_spec.topic}</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    
    <!-- KaTeX for math rendering -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
    
    <!-- D3.js and Chart.js for visualizations -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    
    <!-- Global styles -->
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        
        /* Header Styles */
        .vividoc-header {{
            background: linear-gradient(135deg, #4A90E2 0%, #7CB3E9 100%);
            padding: 20px 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 40px;
        }}
        
        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 40px;
        }}
        
        .brand-name {{
            font-family: 'Poppins', sans-serif;
            font-size: 42px;
            font-weight: 700;
            color: white;
            margin: 0;
            letter-spacing: -1px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex-shrink: 0;
        }}
        
        .brand-tagline {{
            font-family: 'Inter', sans-serif;
            font-size: 15px;
            font-weight: 400;
            color: rgba(255, 255, 255, 0.95);
            margin: 0;
            font-style: italic;
            letter-spacing: 0.3px;
            text-align: right;
            white-space: nowrap;
        }}
        
        /* Main Content */
        .main-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px 40px 20px;
        }}
        
        h1 {{
            font-family: 'Poppins', sans-serif;
            color: #2c3e50;
            margin-bottom: 40px;
            text-align: center;
            font-size: 2.5em;
            font-weight: 600;
        }}
        
        .knowledge-unit {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .text-content {{
            margin-bottom: 30px;
            line-height: 1.8;
            color: #333;
            font-size: 18px;
        }}
        
        .text-content p {{
            margin-bottom: 20px;
        }}
        
        .text-content strong {{
            font-weight: 600;
            color: #000;
        }}
        
        .interactive-content {{
            margin-top: 20px;
        }}
        
        .controls {{
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        
        .controls label {{
            display: inline-block;
            margin-right: 10px;
            font-weight: 500;
        }}
        
        .controls input[type="range"] {{
            width: 200px;
            vertical-align: middle;
        }}
        
        .controls button {{
            padding: 8px 16px;
            background: #4A90E2;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: background 0.3s ease;
        }}
        
        .controls button:hover {{
            background: #357ABD;
        }}
        
        .visualization {{
            min-height: 300px;
            margin-top: 20px;
        }}
        
        @media (max-width: 768px) {{
            .vividoc-header {{
                padding: 25px 15px;
            }}
            
            .header-content {{
                flex-direction: column;
                gap: 12px;
            }}
            
            .brand-name {{
                font-size: 32px;
            }}
            
            .brand-tagline {{
                font-size: 13px;
                text-align: center;
                white-space: normal;
            }}
            
            .main-content {{
                padding: 0 10px 20px 10px;
            }}
            
            .knowledge-unit {{
                padding: 20px;
            }}
            
            h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <!-- ViviDoc Header -->
    <header class="vividoc-header">
        <div class="header-content">
            <h1 class="brand-name">ViviDoc</h1>
            <p class="brand-tagline">Generate Exploratory Explanations Automatically</p>
        </div>
    </header>
    
    <!-- Main Content -->
    <div class="main-content">
        <h1>{doc_spec.topic}</h1>
        
{sections_html}
    </div>
    
    <!-- KaTeX auto-render script -->
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{left: "$$", right: "$$", display: true}},
                    {{left: "$", right: "$", display: false}},
                    {{left: "\\\\[", right: "\\\\]", display: true}},
                    {{left: "\\\\(", right: "\\\\)", display: false}}
                ],
                throwOnError: false
            }});
        }});
    </script>
</body>
</html>
"""

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
