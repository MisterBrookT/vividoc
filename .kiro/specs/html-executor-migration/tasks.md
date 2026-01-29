# Implementation Plan: HTML Executor Migration

## Overview

This plan migrates the Vividoc Executor from Python/matplotlib code generation to HTML/JavaScript generation. The implementation follows an incremental approach: first creating the HTML validator, then updating the executor to use it, adding the document assembler, and finally updating prompts and removing Pyodide dependencies.

## Tasks

- [x] 1. Create HTMLValidator component
  - [x] 1.1 Implement HTMLStructureParser class
    - Create parser that tracks tag stack, root element, and attributes
    - Handle self-closing tags correctly
    - Track unclosed tags for validation
    - _Requirements: 4.1, 4.2_
  
  - [x] 1.2 Implement HTMLValidator class
    - Create validate() method that uses HTMLStructureParser
    - Check for root `<section>` element with class "knowledge-unit"
    - Verify section has id attribute
    - Return descriptive error messages for validation failures
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ]* 1.3 Write property tests for HTMLValidator
    - **Property 7: HTML Validation - Well-Formed Structure**
    - **Validates: Requirements 4.1, 4.2**
  
  - [ ]* 1.4 Write property tests for root element validation
    - **Property 8: HTML Validation - Root Element Check**
    - **Validates: Requirements 4.3**
  
  - [ ]* 1.5 Write property tests for ID attribute validation
    - **Property 9: HTML Validation - ID Attribute Check**
    - **Validates: Requirements 4.4**
  
  - [ ]* 1.6 Write property tests for error messages
    - **Property 10: Validation Error Messages**
    - **Validates: Requirements 4.5**
  
  - [ ]* 1.7 Write unit tests for HTMLValidator
    - Test valid HTML acceptance
    - Test rejection of missing id attribute
    - Test rejection of wrong root element
    - Test rejection of missing class
    - Test unclosed tags detection
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 2. Update Executor to use HTMLValidator
  - [x] 2.1 Modify Executor.validate_code() method
    - Replace exec() call with HTMLValidator.validate()
    - Update return type to match (bool, str) tuple
    - _Requirements: 4.1, 8.3_
  
  - [x] 2.2 Add scope_id parameter to generate_code() method
    - Update method signature to accept scope_id
    - Pass scope_id to prompt generation function
    - _Requirements: 1.2, 1.5_
  
  - [x] 2.3 Update Executor.run() to generate scope IDs
    - Generate scope_id as f"ku{idx}" for each knowledge unit
    - Pass scope_id to generate_code() method
    - _Requirements: 1.2_
  
  - [ ]* 2.4 Write unit tests for updated Executor methods
    - Test validate_code() with valid HTML
    - Test validate_code() with invalid HTML
    - Test scope_id generation and usage
    - _Requirements: 1.2, 4.1_

- [x] 3. Update code generation prompts
  - [x] 3.1 Update CODE_GENERATION_PROMPT in executor_prompt.py
    - Add scope_id parameter to prompt template
    - Emphasize CSS scoping with #{scope_id} prefix
    - Emphasize DOM ID prefixing with {scope_id}- prefix
    - Emphasize IIFE wrapping for JavaScript
    - Include updated example with scope_id
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [x] 3.2 Update CODE_FIX_PROMPT in executor_prompt.py
    - Change from Python to HTML context
    - Add scope_id parameter
    - Include HTML-specific fix instructions
    - _Requirements: 5.1_
  
  - [x] 3.3 Update get_code_generation_prompt() function
    - Add scope_id parameter
    - Pass scope_id to template formatting
    - _Requirements: 1.2, 5.1_
  
  - [x] 3.4 Update get_code_fix_prompt() function
    - Add scope_id parameter
    - Pass scope_id to template formatting
    - _Requirements: 1.2, 5.1_

- [x] 4. Checkpoint - Ensure validation works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Create DocumentAssembler component
  - [x] 5.1 Implement DocumentAssembler class
    - Create HTML_TEMPLATE with complete document structure
    - Include DOCTYPE, html, head, and body tags
    - Add CDN links for D3.js and Chart.js in head
    - Add common CSS for layout and typography
    - Implement assemble() method to concatenate sections
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [ ]* 5.2 Write property tests for DocumentAssembler
    - **Property 11: Document Assembly Order**
    - **Validates: Requirements 6.1**
  
  - [ ]* 5.3 Write property tests for document structure
    - **Property 12: Document Structure Completeness**
    - **Validates: Requirements 6.2**
  
  - [ ]* 5.4 Write property tests for CDN links
    - **Property 13: CDN Links Presence**
    - **Validates: Requirements 6.3**
  
  - [ ]* 5.5 Write property tests for common CSS
    - **Property 14: Common CSS Presence**
    - **Validates: Requirements 6.4**
  
  - [ ]* 5.6 Write unit tests for DocumentAssembler
    - Test section concatenation order
    - Test complete HTML structure
    - Test CDN links presence
    - Test common CSS presence
    - Test file writing
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 6. Integrate DocumentAssembler into workflow
  - [x] 6.1 Add document assembly call to Executor.run() or runner
    - Determine appropriate location (Executor.run() or separate step)
    - Call DocumentAssembler.assemble() after generation completes
    - Save assembled HTML to output path
    - _Requirements: 6.1, 6.2_
  
  - [ ]* 6.2 Write integration tests for full workflow
    - Test end-to-end from DocumentSpec to assembled HTML
    - Verify all sections present in output
    - Verify output is valid HTML5
    - _Requirements: 1.1, 6.1, 6.2, 6.5_

- [x] 7. Update data model documentation
  - [x] 7.1 Update GeneratedKnowledgeUnit field description
    - Change interactive_code description from "Python visualization code" to "HTML visualization code"
    - Update any related comments or docstrings
    - _Requirements: 7.2_
  
  - [ ]* 7.2 Write property tests for data model compatibility
    - **Property 15: HTML Content in interactive_code Field**
    - **Validates: Requirements 7.2**
  
  - [ ]* 7.3 Write property tests for serialization
    - **Property 16: Serialization Round-Trip**
    - **Validates: Requirements 7.4**

- [x] 8. Remove Pyodide dependencies
  - [x] 8.1 Remove Pyodide imports from codebase
    - Search for and remove any Pyodide import statements
    - Remove Pyodide initialization code
    - _Requirements: 8.1, 8.2_
  
  - [x] 8.2 Update requirements.txt or pyproject.toml
    - Remove Pyodide-related packages
    - Verify no other code depends on removed packages
    - _Requirements: 8.4_
  
  - [ ]* 8.3 Run full test suite to verify no regressions
    - Ensure all existing tests still pass
    - Verify no import errors
    - _Requirements: 8.1, 8.2, 8.3_

- [ ] 9. Add property tests for generated HTML structure
  - [ ]* 9.1 Write property tests for HTML section structure
    - **Property 1: HTML Section Structure**
    - **Validates: Requirements 1.1, 1.2**
  
  - [ ]* 9.2 Write property tests for CSS scoping
    - **Property 2: CSS Scoping**
    - **Validates: Requirements 1.3, 2.1**
  
  - [ ]* 9.3 Write property tests for JavaScript IIFE wrapping
    - **Property 3: JavaScript IIFE Wrapping**
    - **Validates: Requirements 1.4, 2.2**
  
  - [ ]* 9.4 Write property tests for DOM ID prefixing
    - **Property 4: DOM ID Prefixing**
    - **Validates: Requirements 1.5, 2.3**
  
  - [ ]* 9.5 Write property tests for no global scope pollution
    - **Property 5: No Global Scope Pollution**
    - **Validates: Requirements 2.5**
  
  - [ ]* 9.6 Write property tests for interactive controls presence
    - **Property 6: Interactive Controls Presence**
    - **Validates: Requirements 3.4**

- [x] 10. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties across many generated inputs
- Unit tests validate specific examples and edge cases
- The migration maintains backward compatibility with existing data models
- HTMLValidator replaces Python exec() for safer, faster validation
- DocumentAssembler creates complete, standalone HTML documents
