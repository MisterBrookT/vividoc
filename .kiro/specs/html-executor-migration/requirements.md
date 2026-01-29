# Requirements Document

## Introduction

This document specifies the requirements for migrating the Vividoc Executor from generating Python code with matplotlib visualizations to generating self-contained HTML sections with inline CSS and JavaScript for interactive components.

## Glossary

- **Executor**: The component responsible for generating interactive code for knowledge units
- **Knowledge_Unit**: A discrete educational concept with associated interactive visualization
- **HTML_Section**: A self-contained `<section>` element containing styles, markup, and scripts
- **Scope_ID**: A unique identifier (ku1, ku2, etc.) used to prevent conflicts between sections
- **Validator**: The component that checks generated code for correctness
- **Document_Assembler**: The component that combines multiple HTML sections into a complete document

## Requirements

### Requirement 1: HTML Section Generation

**User Story:** As a developer, I want the Executor to generate HTML sections instead of Python code, so that visualizations can run directly in browsers without server-side execution.

#### Acceptance Criteria

1. WHEN the Executor generates code for a knowledge unit, THE Executor SHALL create an HTML `<section>` element with class "knowledge-unit"
2. WHEN generating an HTML section, THE Executor SHALL assign a unique Scope_ID to the section's id attribute
3. THE Executor SHALL include inline `<style>` tags within each section with CSS rules scoped to the Scope_ID
4. THE Executor SHALL include inline `<script>` tags within each section wrapped in self-executing functions
5. WHEN generating JavaScript code, THE Executor SHALL use the Scope_ID to namespace all DOM element IDs within the section

### Requirement 2: Self-Contained Section Structure

**User Story:** As a developer, I want each HTML section to be self-contained, so that multiple sections can be combined without conflicts.

#### Acceptance Criteria

1. WHEN an HTML section contains CSS rules, THE Executor SHALL prefix all selectors with the Scope_ID to prevent style leakage
2. WHEN an HTML section contains JavaScript, THE Executor SHALL wrap all code in an immediately-invoked function expression (IIFE)
3. THE Executor SHALL ensure all DOM element IDs within a section include the Scope_ID as a prefix
4. WHEN multiple sections are concatenated, THE System SHALL maintain independent functionality for each section
5. THE Executor SHALL NOT create global JavaScript variables or functions that could conflict between sections

### Requirement 3: Interactive Component Support

**User Story:** As a content creator, I want to use modern JavaScript libraries for visualizations, so that I can create rich interactive experiences.

#### Acceptance Criteria

1. THE Executor SHALL support generation of vanilla JavaScript code without external dependencies
2. WHERE D3.js is needed, THE Executor SHALL generate code compatible with D3.js loaded via CDN
3. WHERE Chart.js is needed, THE Executor SHALL generate code compatible with Chart.js loaded via CDN
4. WHEN generating interactive controls, THE Executor SHALL create standard HTML input elements (sliders, buttons, text inputs)
5. WHEN user interactions occur, THE JavaScript SHALL update visualizations in real-time without page reload

### Requirement 4: HTML Validation

**User Story:** As a developer, I want generated HTML to be validated, so that malformed code is caught before document assembly.

#### Acceptance Criteria

1. WHEN the Validator receives HTML code, THE Validator SHALL parse it to verify well-formed structure
2. THE Validator SHALL verify that all opening tags have matching closing tags
3. THE Validator SHALL verify that the root element is a `<section>` tag with class "knowledge-unit"
4. THE Validator SHALL verify that the section has a unique id attribute
5. IF validation fails, THEN THE Validator SHALL return a descriptive error message indicating the issue

### Requirement 5: Prompt Template Updates

**User Story:** As a developer, I want the code generation prompt to request HTML output, so that the LLM generates the correct format.

#### Acceptance Criteria

1. THE System SHALL update CODE_GENERATION_PROMPT to request HTML section generation instead of Python code
2. THE CODE_GENERATION_PROMPT SHALL include examples of properly structured HTML sections
3. THE CODE_GENERATION_PROMPT SHALL specify that CSS must be scoped using the Scope_ID
4. THE CODE_GENERATION_PROMPT SHALL specify that JavaScript must use IIFEs to avoid global scope pollution
5. THE CODE_GENERATION_PROMPT SHALL list available JavaScript libraries (D3.js, Chart.js) and their CDN availability

### Requirement 6: Document Assembly

**User Story:** As a user, I want all knowledge unit sections combined into a complete HTML document, so that I can view the entire educational content in a browser.

#### Acceptance Criteria

1. WHEN assembling a document, THE Document_Assembler SHALL concatenate all HTML sections in order
2. THE Document_Assembler SHALL wrap concatenated sections in a complete HTML document structure with `<!DOCTYPE html>`, `<html>`, `<head>`, and `<body>` tags
3. THE Document_Assembler SHALL include CDN links in the `<head>` for D3.js and Chart.js
4. THE Document_Assembler SHALL include common CSS in the `<head>` for responsive layout and typography
5. THE assembled document SHALL be valid HTML5 that renders correctly in modern browsers

### Requirement 7: Data Model Compatibility

**User Story:** As a developer, I want to maintain existing data structures, so that the migration requires minimal changes to the codebase.

#### Acceptance Criteria

1. THE System SHALL continue using the GeneratedKnowledgeUnit data model
2. THE interactive_code field SHALL store HTML content instead of Python code
3. THE code_validated field SHALL continue to indicate validation status (True/False)
4. WHEN serializing GeneratedKnowledgeUnit to JSON, THE System SHALL preserve all existing fields
5. THE System SHALL NOT require changes to data persistence or retrieval logic

### Requirement 8: Pyodide Removal

**User Story:** As a developer, I want to remove Pyodide dependencies, so that the system is simpler and has fewer dependencies.

#### Acceptance Criteria

1. THE System SHALL NOT use Pyodide for code execution
2. THE System SHALL remove all Pyodide imports and initialization code
3. THE Validator SHALL NOT use Python exec() for validation
4. THE System SHALL reduce package dependencies by removing Pyodide-related packages
5. THE System SHALL maintain or improve validation speed compared to Pyodide-based validation
