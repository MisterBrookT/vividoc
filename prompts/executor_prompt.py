"""Prompt templates for Executor V2 - Fragment-based generation."""

# Stage 1: Generate text content fragment only
FRAGMENT_STAGE1_PROMPT = """You are an expert educational content writer creating an interactive document about "{topic}".

=== COMPLETED SECTIONS (for style reference only, DO NOT modify) ===
{completed_sections}

=== CURRENT TASK ===
Section ID: {scope_id}
Section Title: {unit_content}
Content Description: {text_description}

=== REQUIREMENTS ===
1. Maintain the SAME writing style, tone, and detail level as completed sections
2. Ensure content difficulty progresses naturally from previous sections
3. Use HTML formatting:
   - <p> tags for paragraphs
   - <strong> for emphasis
   - <em> for italics
   - KaTeX syntax for math: $\\pi$, $E=mc^2$, $\\frac{{a}}{{b}}$
4. ONLY return the HTML fragment for the text content
5. DO NOT include <div class="text-content"> tags
6. DO NOT include any other sections

=== OUTPUT FORMAT ===
Return ONLY the HTML fragment (no div wrapper):

<p>First paragraph with <strong>emphasis</strong> and math $\\pi$.</p>
<p>Second paragraph explaining the concept.</p>
<p>Formula: $E = mc^2$</p>

Now generate the text content fragment for section {scope_id}:
"""


# Stage 2: Generate interactive content fragment only
FRAGMENT_STAGE2_PROMPT = """You are an expert at creating interactive educational visualizations for a document about "{topic}".

=== COMPLETED SECTIONS (for style reference only, DO NOT modify) ===
{completed_sections}

=== CURRENT SECTION'S TEXT CONTENT ===
{current_text_content}

=== CURRENT TASK ===
Section ID: {scope_id}
Interactive Description: {interaction_description}

=== REQUIREMENTS ===
1. Create an interactive visualization that COMPLEMENTS the text content above
2. Maintain consistent interaction design style with previous sections
3. Include three parts in order:
   a) <style> tag: CSS styles (all selectors prefixed with #{scope_id})
   b) HTML structure: controls, visualization containers
   c) <script> tag: JavaScript logic (wrapped in IIFE)
4. All DOM IDs must use {scope_id}- prefix (e.g., {scope_id}-slider)
5. You can use D3.js, Chart.js (already loaded in document)
6. ONLY return the HTML fragment for the interactive content
7. DO NOT include <div class="interactive-content"> tags
8. DO NOT include any other sections

=== IMPORTANT NOTES ===
- When using Chart.js with maintainAspectRatio: false, the canvas container MUST have explicit height
- All JavaScript must be wrapped in IIFE: (function() {{ ... }})()
- Use {scope_id}- prefix for all IDs to avoid conflicts

=== OUTPUT FORMAT ===
Return ONLY the HTML fragment (no div wrapper):

<style>
    #{scope_id} .controls {{ margin: 20px 0; }}
    #{scope_id} .viz {{ min-height: 300px; }}
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
        
        function update() {{
            valueSpan.textContent = slider.value;
            // Update visualization
        }}
        
        slider.addEventListener('input', update);
        update();
    }})();
</script>

Now generate the interactive content fragment for section {scope_id}:
"""


def get_fragment_stage1_prompt(
    topic: str,
    completed_sections: str,
    scope_id: str,
    unit_content: str,
    text_description: str,
) -> str:
    """Generate Stage 1 prompt for text content fragment."""
    return FRAGMENT_STAGE1_PROMPT.format(
        topic=topic,
        completed_sections=completed_sections,
        scope_id=scope_id,
        unit_content=unit_content,
        text_description=text_description,
    )


def get_fragment_stage2_prompt(
    topic: str,
    completed_sections: str,
    scope_id: str,
    current_text_content: str,
    interaction_description: str,
) -> str:
    """Generate Stage 2 prompt for interactive content fragment."""
    return FRAGMENT_STAGE2_PROMPT.format(
        topic=topic,
        completed_sections=completed_sections,
        scope_id=scope_id,
        current_text_content=current_text_content,
        interaction_description=interaction_description,
    )
