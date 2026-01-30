"""Prompt templates for Executor agent."""

# Stage 1: Fill text content in HTML
STAGE1_TEXT_PROMPT = """You are an expert educational content writer. Fill the text content for a specific section in the given HTML document.

Current complete HTML document:
```html
{current_html}
```

Target Section ID: {scope_id}

Text content description:
{text_description}

Task:
1. Find the <section> tag with id="{scope_id}"
2. Fill educational text content inside its <div class="text-content">
3. Use HTML formatting:
   - Use <p> tags for paragraphs
   - Use <strong> tags for emphasis
   - Use KaTeX syntax for math: $\\pi$, $$E=mc^2$$
4. Keep all other sections unchanged
5. Maintain the complete HTML document structure

Example text content:
```html
<div class="text-content">
    <p>The number $\\pi$ (pi) is a mathematical constant.</p>
    <p>It represents the ratio of a circle's <strong>circumference</strong> to its <strong>diameter</strong>.</p>
    <p>The formula is: $$\\pi = \\frac{{C}}{{d}}$$</p>
</div>
```

Return the complete HTML document with the text content filled in for section {scope_id}.
"""

# Stage 2: Add interactive content in HTML
STAGE2_INTERACTIVE_PROMPT = """You are an expert at creating interactive educational visualizations. Add interactive content for a specific section in the given HTML document.

Current complete HTML document (with text content already filled):
```html
{current_html}
```

Target Section ID: {scope_id}

Interactive content description:
{interaction_description}

Task:
1. Find the <section> tag with id="{scope_id}"
2. Add interactive visualization inside its <div class="interactive-content">
3. Include:
   - <style> tag: CSS styles (all selectors prefixed with #{scope_id})
   - HTML structure: controls, visualization containers
   - <script> tag: JavaScript logic (wrapped in IIFE)
4. The interactive content should complement the text content in this section
5. All DOM IDs must use {scope_id}- prefix (e.g., {scope_id}-slider)
6. You can use D3.js, Chart.js (already loaded)
7. Keep all other sections unchanged

IMPORTANT - Chart.js Best Practice:
When using Chart.js with maintainAspectRatio: false, the canvas container MUST have an explicit height (e.g., height: 300px). Otherwise, the chart will expand infinitely.

Example interactive content:
```html
<div class="interactive-content">
    <style>
        #{scope_id} .controls {{ margin: 20px 0; }}
        #{scope_id} .viz {{ min-height: 300px; background: #f9f9f9; }}
    </style>
    
    <div class="controls">
        <label for="{scope_id}-slider">Value:</label>
        <input id="{scope_id}-slider" type="range" min="1" max="10" value="5">
        <span id="{scope_id}-value">5</span>
    </div>
    <div class="viz" id="{scope_id}-viz"></div>
    
    <script>
        (function() {{
            const slider = document.getElementById('{scope_id}-slider');
            const valueSpan = document.getElementById('{scope_id}-value');
            const viz = document.getElementById('{scope_id}-viz');
            
            function update() {{
                valueSpan.textContent = slider.value;
                // Update visualization
            }}
            
            slider.addEventListener('input', update);
            update();
        }})();
    </script>
</div>
```

Return the complete HTML document with the interactive content added for section {scope_id}.
"""


def get_stage1_prompt(current_html: str, scope_id: str, text_description: str) -> str:
    """Generate Stage 1 prompt for filling text content."""
    return STAGE1_TEXT_PROMPT.format(
        current_html=current_html, scope_id=scope_id, text_description=text_description
    )


def get_stage2_prompt(
    current_html: str, scope_id: str, interaction_description: str
) -> str:
    """Generate Stage 2 prompt for adding interactive content."""
    return STAGE2_INTERACTIVE_PROMPT.format(
        current_html=current_html,
        scope_id=scope_id,
        interaction_description=interaction_description,
    )
