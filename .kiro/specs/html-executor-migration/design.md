# Design Document: HTML Executor Migration

## Overview

This design describes the migration of the Vividoc Executor from generating Python code with matplotlib visualizations to generating self-contained HTML sections with inline CSS and JavaScript. The migration maintains the existing data models and workflow while replacing Python code generation and validation with HTML generation and parsing.

The key architectural change is replacing the `exec()`-based Python validation with HTML parsing validation, and updating the code generation prompt to produce HTML instead of Python. The system will continue to use the same LLM-based generation approach but with different output format and validation logic.

## Architecture

### Current Architecture
```
DocumentSpec → Executor.generate_code() → Python code → exec() validation → GeneratedDocument
```

### New Architecture
```
DocumentSpec → Executor.generate_code() → HTML section → HTML parsing validation → GeneratedDocument
```

The migration affects three main components:
1. **Code Generation**: Update prompts to request HTML instead of Python
2. **Validation**: Replace `exec()` with HTML parsing
3. **Document Assembly**: Add new component to combine sections into complete HTML document

## Components and Interfaces

### 1. Executor (Modified)

The `Executor` class remains the main orchestrator but with updated validation logic.

**Modified Methods:**

```python
def generate_code(self, interaction_description: str, scope_id: str) -> str:
    """Generate interactive HTML section.
    
    Args:
        interaction_description: Description of the interactive component
        scope_id: Unique identifier for this section (e.g., "ku1", "ku2")
    
    Returns:
        HTML section as string
    """
    prompt = get_code_generation_prompt(interaction_description, scope_id)
    html_code = self.llm_client.call_text_generation(
        model=self.config.llm_model,
        prompt=prompt
    )
    return html_code

def validate_code(self, html_code: str) -> tuple[bool, str]:
    """Validate HTML structure and syntax.
    
    Args:
        html_code: HTML section to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    validator = HTMLValidator()
    return validator.validate(html_code)
```

**Scope ID Generation:**

The executor needs to generate unique scope IDs for each knowledge unit. This can be done using the knowledge unit's index:

```python
def run(self, doc_spec: DocumentSpec) -> GeneratedDocument:
    for idx, ku_spec in enumerate(doc_spec.knowledge_units, 1):
        scope_id = f"ku{idx}"
        code = self.generate_code(ku_spec.interaction_description, scope_id)
        # ... rest of logic
```

### 2. HTMLValidator (New Component)

A new component responsible for validating generated HTML sections.

**Interface:**

```python
class HTMLValidator:
    """Validates HTML sections for structure and correctness."""
    
    def validate(self, html_code: str) -> tuple[bool, str]:
        """Validate HTML section.
        
        Checks:
        - Well-formed HTML structure
        - Root element is <section> with class "knowledge-unit"
        - Section has an id attribute
        - All opening tags have matching closing tags
        
        Args:
            html_code: HTML section to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
```

**Implementation Approach:**

Use Python's built-in `html.parser.HTMLParser` to parse and validate HTML structure:

```python
from html.parser import HTMLParser
from typing import List, Tuple

class HTMLValidator:
    def validate(self, html_code: str) -> tuple[bool, str]:
        parser = HTMLStructureParser()
        try:
            parser.feed(html_code)
            
            # Check root element
            if not parser.root_tag:
                return False, "No root element found"
            
            if parser.root_tag != "section":
                return False, f"Root element must be <section>, found <{parser.root_tag}>"
            
            if "knowledge-unit" not in parser.root_classes:
                return False, "Root <section> must have class 'knowledge-unit'"
            
            if not parser.root_id:
                return False, "Root <section> must have an id attribute"
            
            # Check for unclosed tags
            if parser.unclosed_tags:
                return False, f"Unclosed tags: {', '.join(parser.unclosed_tags)}"
            
            return True, ""
            
        except Exception as e:
            return False, f"HTML parsing error: {str(e)}"

class HTMLStructureParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag_stack: List[str] = []
        self.root_tag: str = None
        self.root_classes: List[str] = []
        self.root_id: str = None
        self.unclosed_tags: List[str] = []
    
    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]):
        if not self.root_tag:
            self.root_tag = tag
            attrs_dict = dict(attrs)
            self.root_id = attrs_dict.get("id", "")
            class_attr = attrs_dict.get("class", "")
            self.root_classes = class_attr.split() if class_attr else []
        
        # Track self-closing tags differently
        if tag not in ["img", "br", "hr", "input", "meta", "link"]:
            self.tag_stack.append(tag)
    
    def handle_endtag(self, tag: str):
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
        elif tag not in ["img", "br", "hr", "input", "meta", "link"]:
            self.unclosed_tags.append(tag)
    
    def close(self):
        super().close()
        if self.tag_stack:
            self.unclosed_tags.extend(self.tag_stack)
```

### 3. DocumentAssembler (New Component)

A new component responsible for combining HTML sections into a complete HTML document.

**Interface:**

```python
class DocumentAssembler:
    """Assembles HTML sections into a complete HTML document."""
    
    def assemble(self, generated_doc: GeneratedDocument, output_path: str) -> None:
        """Assemble knowledge units into complete HTML document.
        
        Args:
            generated_doc: Generated document with HTML sections
            output_path: Path to save the assembled HTML file
        """
        pass
```

**Implementation:**

```python
class DocumentAssembler:
    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic}</title>
    
    <!-- External Libraries -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    
    <!-- Common Styles -->
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        h1 {{
            color: #2c3e50;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .knowledge-unit {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        
        .controls button:hover {{
            background: #0056b3;
        }}
        
        .visualization {{
            min-height: 300px;
            margin-top: 20px;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            
            .knowledge-unit {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <h1>{topic}</h1>
    
    {sections}
    
</body>
</html>
"""
    
    def assemble(self, generated_doc: GeneratedDocument, output_path: str) -> None:
        # Concatenate all HTML sections
        sections = "\n\n".join(
            ku.interactive_code 
            for ku in generated_doc.knowledge_units
        )
        
        # Fill template
        html_content = self.HTML_TEMPLATE.format(
            topic=generated_doc.topic,
            sections=sections
        )
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
```

### 4. Prompt Updates

The `CODE_GENERATION_PROMPT` needs to be updated to include the scope_id parameter and emphasize HTML generation requirements.

**Updated Prompt:**

```python
CODE_GENERATION_PROMPT = """You are an expert at creating interactive educational visualizations using HTML, CSS, and JavaScript. Generate a self-contained HTML section based on the following description.

Description: {interaction_description}

IMPORTANT: Use the section ID "{scope_id}" for this component.

Generate HTML code that:
- Uses a <section> element with class="knowledge-unit" and id="{scope_id}"
- Includes inline CSS in <style> tags with all selectors prefixed with #{scope_id}
- Includes inline JavaScript in <script> tags wrapped in an IIFE: (function() {{ ... }})()
- All DOM element IDs must be prefixed with "{scope_id}-" (e.g., "{scope_id}-slider", "{scope_id}-viz")
- Uses modern JavaScript (ES6+) and can use D3.js, Chart.js, or vanilla JS
- D3.js and Chart.js are available via CDN (already loaded in the page)
- Includes clear labels and interactive controls (sliders, buttons, inputs)
- Is fully self-contained with no global variables or functions

Example structure:
```html
<section class="knowledge-unit" id="{scope_id}">
  <style>
    #{scope_id} .controls {{ margin: 20px 0; }}
    #{scope_id} .visualization {{ min-height: 300px; }}
  </style>
  
  <div class="controls">
    <label for="{scope_id}-input">Input:</label>
    <input id="{scope_id}-input" type="range" min="1" max="100" value="50">
    <span id="{scope_id}-value">50</span>
  </div>
  
  <div class="visualization" id="{scope_id}-viz"></div>
  
  <script>
    (function() {{
      const input = document.getElementById('{scope_id}-input');
      const value = document.getElementById('{scope_id}-value');
      const viz = document.getElementById('{scope_id}-viz');
      
      function update() {{
        value.textContent = input.value;
        // Update visualization
      }}
      
      input.addEventListener('input', update);
      update();
    }})();
  </script>
</section>
```

Generate only the HTML code, no explanations or markdown formatting.
"""
```

**Updated Fix Prompt:**

```python
CODE_FIX_PROMPT = """The following HTML code has validation errors. Fix the code to make it valid.

Original code:
```html
{code}
```

Error message:
{error}

Generate the fixed HTML code that resolves this error. Ensure:
- The root element is <section class="knowledge-unit" id="{scope_id}">
- All CSS selectors are prefixed with #{scope_id}
- All DOM element IDs are prefixed with "{scope_id}-"
- JavaScript is wrapped in an IIFE
- All HTML tags are properly closed

Generate only the corrected HTML code, no explanations.
"""
```

## Data Models

No changes to existing data models. The `GeneratedKnowledgeUnit.interactive_code` field will store HTML content instead of Python code, but the field definition remains the same.

```python
class GeneratedKnowledgeUnit(BaseModel):
    """Generated content for a single knowledge unit from Executor."""
    id: str = Field(description="Unique identifier matching the spec")
    unit_content: str = Field(description="Brief summary from spec")
    text_content: str = Field(description="Generated educational text")
    interactive_code: str = Field(description="Generated HTML visualization code")  # Content changes, not structure
    code_validated: bool = Field(description="Whether the code has been validated")
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: HTML Section Structure
*For any* generated HTML code from the Executor, parsing it should yield a root `<section>` element with class "knowledge-unit" and a non-empty id attribute.
**Validates: Requirements 1.1, 1.2**

### Property 2: CSS Scoping
*For any* generated HTML section with a scope ID, all CSS selectors in the `<style>` tag should be prefixed with `#{scope_id}` to prevent style leakage.
**Validates: Requirements 1.3, 2.1**

### Property 3: JavaScript IIFE Wrapping
*For any* generated HTML section containing JavaScript, the `<script>` tag content should match the IIFE pattern `(function() { ... })()` to avoid global scope pollution.
**Validates: Requirements 1.4, 2.2**

### Property 4: DOM ID Prefixing
*For any* generated HTML section with scope ID, all DOM element IDs within the section should start with the scope ID prefix (e.g., "ku1-").
**Validates: Requirements 1.5, 2.3**

### Property 5: No Global Scope Pollution
*For any* generated HTML section, parsing the JavaScript should reveal no variable or function declarations outside of IIFEs (no global `var`, `let`, `const`, or `function` declarations).
**Validates: Requirements 2.5**

### Property 6: Interactive Controls Presence
*For any* generated HTML section intended to be interactive, the HTML should contain at least one standard input element (input, button, select, or textarea).
**Validates: Requirements 3.4**

### Property 7: HTML Validation - Well-Formed Structure
*For any* HTML string passed to the validator, if it contains mismatched opening/closing tags, the validator should return `(False, error_message)` where error_message is non-empty.
**Validates: Requirements 4.1, 4.2**

### Property 8: HTML Validation - Root Element Check
*For any* HTML string passed to the validator, if the root element is not a `<section>` tag with class "knowledge-unit", the validator should return `(False, error_message)`.
**Validates: Requirements 4.3**

### Property 9: HTML Validation - ID Attribute Check
*For any* HTML string passed to the validator, if the root `<section>` element lacks an id attribute, the validator should return `(False, error_message)`.
**Validates: Requirements 4.4**

### Property 10: Validation Error Messages
*For any* invalid HTML that fails validation, the validator should return an error message that is non-empty and contains information about the validation failure.
**Validates: Requirements 4.5**

### Property 11: Document Assembly Order
*For any* GeneratedDocument with N knowledge units, assembling the document should produce HTML where the sections appear in the same order as the knowledge units list.
**Validates: Requirements 6.1**

### Property 12: Document Structure Completeness
*For any* assembled HTML document, parsing it should reveal the presence of `<!DOCTYPE html>`, `<html>`, `<head>`, and `<body>` tags.
**Validates: Requirements 6.2**

### Property 13: CDN Links Presence
*For any* assembled HTML document, the `<head>` section should contain `<script>` tags with src attributes pointing to D3.js and Chart.js CDNs.
**Validates: Requirements 6.3**

### Property 14: Common CSS Presence
*For any* assembled HTML document, the `<head>` section should contain a `<style>` tag with CSS rules for common layout and typography.
**Validates: Requirements 6.4**

### Property 15: HTML Content in interactive_code Field
*For any* GeneratedKnowledgeUnit created by the Executor, the interactive_code field should contain a string that can be parsed as HTML with a root `<section>` element.
**Validates: Requirements 7.2**

### Property 16: Serialization Round-Trip
*For any* valid GeneratedKnowledgeUnit object, serializing it to JSON and then deserializing should produce an equivalent object with all fields preserved.
**Validates: Requirements 7.4**

## Error Handling

### Validation Errors

When HTML validation fails, the system should:
1. Return a descriptive error message indicating the specific issue
2. Attempt to fix the HTML using the LLM with the updated fix prompt
3. Retry validation up to `max_code_fix_attempts` times
4. If all attempts fail, mark `code_validated=False` and continue

### Parsing Errors

If the HTMLParser encounters malformed HTML that causes an exception:
1. Catch the exception and return `(False, f"HTML parsing error: {str(e)}")`
2. Pass the error to the fix prompt for correction

### Assembly Errors

If document assembly fails (e.g., file write error):
1. Log the error with details
2. Raise the exception to the caller (fail fast)

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs

### Property-Based Testing

Use the `hypothesis` library for Python to implement property-based tests. Each property test should:
- Run a minimum of 100 iterations
- Reference its design document property in a comment
- Use the tag format: `# Feature: html-executor-migration, Property N: [property text]`

**Example Property Test:**

```python
from hypothesis import given, strategies as st
import pytest

# Feature: html-executor-migration, Property 1: HTML Section Structure
@given(st.text(min_size=10, max_size=500))
def test_property_html_section_structure(interaction_description):
    """For any generated HTML, it should have proper section structure."""
    executor = Executor(ExecutorConfig())
    scope_id = "ku1"
    
    html_code = executor.generate_code(interaction_description, scope_id)
    
    # Parse and verify structure
    parser = HTMLStructureParser()
    parser.feed(html_code)
    
    assert parser.root_tag == "section"
    assert "knowledge-unit" in parser.root_classes
    assert parser.root_id != ""
```

### Unit Testing

Unit tests should focus on:
1. **Specific examples**: Test with known good HTML sections
2. **Edge cases**: Empty sections, sections with no JavaScript, sections with no CSS
3. **Error conditions**: Malformed HTML, missing required attributes
4. **Integration**: Test the full flow from generation to validation to assembly

**Example Unit Tests:**

```python
def test_validator_accepts_valid_html():
    """Test that validator accepts properly structured HTML."""
    valid_html = '''
    <section class="knowledge-unit" id="ku1">
        <style>#ku1 .test { color: red; }</style>
        <div id="ku1-content">Test</div>
        <script>(function() { console.log("test"); })();</script>
    </section>
    '''
    validator = HTMLValidator()
    is_valid, error = validator.validate(valid_html)
    assert is_valid
    assert error == ""

def test_validator_rejects_missing_id():
    """Test that validator rejects section without id."""
    invalid_html = '<section class="knowledge-unit"><div>Test</div></section>'
    validator = HTMLValidator()
    is_valid, error = validator.validate(invalid_html)
    assert not is_valid
    assert "id" in error.lower()

def test_document_assembly_order():
    """Test that sections appear in correct order."""
    doc = GeneratedDocument(
        topic="Test Topic",
        knowledge_units=[
            GeneratedKnowledgeUnit(
                id="ku1",
                unit_content="Unit 1",
                text_content="Text 1",
                interactive_code='<section class="knowledge-unit" id="ku1">Content 1</section>',
                code_validated=True
            ),
            GeneratedKnowledgeUnit(
                id="ku2",
                unit_content="Unit 2",
                text_content="Text 2",
                interactive_code='<section class="knowledge-unit" id="ku2">Content 2</section>',
                code_validated=True
            )
        ]
    )
    
    assembler = DocumentAssembler()
    output_path = "test_output.html"
    assembler.assemble(doc, output_path)
    
    with open(output_path, 'r') as f:
        content = f.read()
    
    # Verify order
    pos1 = content.find('id="ku1"')
    pos2 = content.find('id="ku2"')
    assert pos1 < pos2
```

### Test Coverage Goals

- **HTMLValidator**: 100% coverage of validation logic
- **DocumentAssembler**: 100% coverage of assembly logic
- **Executor modifications**: Test all new/modified methods
- **Property tests**: All 16 properties implemented as property-based tests
- **Integration tests**: End-to-end flow from spec to assembled document
