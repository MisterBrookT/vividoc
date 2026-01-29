# Implementation Plan: Vividoc System

## Overview

This implementation plan breaks down the Vividoc System into incremental coding tasks. The system will be built in phases: first the data models and LLM client, then each agent (Planner, Executor, Evaluator), followed by the pipeline orchestration, CLI interface, and finally the Web UI. Each task builds on previous work and includes testing to validate functionality early.

## Tasks

- [x] 1. Set up data models and LLM client infrastructure
  - [x] 1.1 Create Pydantic data models
    - Define KnowledgeUnitSpec, DocumentSpec, GeneratedKnowledgeUnit, GeneratedDocument, and EvaluationFeedback models in vividoc/models.py
    - Add field validation and type hints
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [ ]* 1.2 Write property test for Pydantic model serialization
    - **Property 3: Pydantic Model Serialization Round-Trip**
    - **Validates: Requirements 1.6, 5.5, 5.6**
  
  - [x] 1.3 Extend LLM client with structured output support
    - Add call_structured_output method to LLMClient in vividoc/utils/llm/client.py
    - Accept Pydantic model schemas and return typed instances
    - Configure response_mime_type and response_json_schema
    - _Requirements: 4.3, 4.4, 4.5, 4.6_
  
  - [ ]* 1.4 Write property test for LLM client type safety
    - **Property 8: LLM Client Type Safety**
    - **Validates: Requirements 4.5, 4.6**

- [x] 2. Implement Planner Agent
  - [x] 2.1 Create PlannerConfig dataclass
    - Define configuration with llm_provider, llm_model, and output_path fields in vividoc/planner.py
    - Set default values (google, gemini-2.5-pro)
    - _Requirements: 1.7_
  
  - [x] 2.2 Implement Planner.run() method
    - Accept topic string as input
    - Call LLM with structured output for DocumentSpec
    - Generate knowledge units with unique IDs
    - Return validated DocumentSpec
    - _Requirements: 1.1, 1.2, 1.3, 1.8_
  
  - [x] 2.3 Create prompt template for document spec generation
    - Write prompt that includes examples of good knowledge units
    - Emphasize self-contained descriptions for text and interaction
    - Store in prompts/planner_prompt.py
    - _Requirements: 1.4, 1.5_
  
  - [ ]* 2.4 Write property test for document spec completeness
    - **Property 1: Document Spec Completeness**
    - **Validates: Requirements 1.1, 1.3**
  
  - [ ]* 2.5 Write property test for knowledge unit ID uniqueness
    - **Property 2: Knowledge Unit ID Uniqueness**
    - **Validates: Requirements 1.2**
  
  - [ ]* 2.6 Write unit test for "What is π?" example
    - Test with the specific example from requirements
    - Verify DocumentSpec structure and content
    - _Requirements: 1.1, 1.2, 1.3_

- [ ] 3. Checkpoint - Ensure Planner tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement Executor Agent
  - [x] 4.1 Create ExecutorConfig dataclass
    - Define configuration with llm_provider, llm_model, max_code_fix_attempts, code_timeout_seconds, and output_path
    - Set default values
    - _Requirements: 2.7_
  
  - [x] 4.2 Implement Executor.generate_text() method
    - Accept text_description as input
    - Call LLM to generate educational text content
    - Return generated text string
    - _Requirements: 2.2_
  
  - [x] 4.3 Implement Executor.generate_code() method
    - Accept interaction_description as input
    - Call LLM to generate Python visualization code
    - Return generated code string
    - _Requirements: 2.3, 2.8_
  
  - [x] 4.4 Implement Executor.validate_code() method
    - Execute code in isolated environment using exec()
    - Capture stdout, stderr, and exceptions
    - Return tuple of (success: bool, error_message: str)
    - Use 30-second timeout
    - _Requirements: 2.4, 10.1, 10.2, 10.3_
  
  - [x] 4.5 Implement Executor.fix_code() method
    - Accept code and error message as input
    - Call LLM with error context to generate fixed code
    - Return fixed code string
    - _Requirements: 2.5, 10.4_
  
  - [x] 4.6 Implement Executor.run() method
    - Accept DocumentSpec as input
    - Process each knowledge unit sequentially
    - For each unit: generate text, generate code, validate code, fix if needed (max 3 attempts)
    - Return GeneratedDocument with all units populated
    - _Requirements: 2.1, 2.6, 10.5, 10.6_
  
  - [ ]* 4.7 Write property test for executor output completeness
    - **Property 4: Executor Output Completeness**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.6**
  
  - [ ]* 4.8 Write property test for code validation state consistency
    - **Property 5: Code Validation State Consistency**
    - **Validates: Requirements 2.4, 2.8, 10.6**
  
  - [ ]* 4.9 Write property test for code execution error capture
    - **Property 10: Code Execution Error Capture**
    - **Validates: Requirements 10.3**
  
  - [ ]* 4.10 Write unit tests for code validation edge cases
    - Test syntax errors, runtime errors, timeout scenarios
    - Test bug-fixing loop with mock LLM responses
    - _Requirements: 2.4, 2.5, 10.1, 10.2, 10.3_

- [ ] 5. Checkpoint - Ensure Executor tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [-] 6. Implement Evaluator Agent
  - [x] 6.1 Create EvaluatorConfig dataclass
    - Define configuration with llm_provider, llm_model, and output_path
    - Set default values
    - _Requirements: 3.6_
  
  - [x] 6.2 Implement Evaluator.check_coherence() method
    - Accept GeneratedDocument as input
    - Call LLM to evaluate text fluency and logical flow
    - Return coherence assessment string
    - _Requirements: 3.1, 3.2_
  
  - [x] 6.3 Implement Evaluator.check_components() method
    - Accept GeneratedDocument as input
    - Validate each interactive component's code syntax
    - Return list of issues found (empty if all valid)
    - _Requirements: 3.3_
  
  - [x] 6.4 Implement Evaluator.run() method
    - Accept GeneratedDocument as input
    - Call check_coherence() and check_components()
    - Generate EvaluationFeedback with overall_coherence, component_issues, and requires_revision
    - _Requirements: 3.4, 3.5_
  
  - [ ]* 6.5 Write property test for evaluator feedback completeness
    - **Property 6: Evaluator Feedback Completeness**
    - **Validates: Requirements 3.4**
  
  - [ ]* 6.6 Write property test for evaluation coverage
    - **Property 7: Evaluation Coverage**
    - **Validates: Requirements 3.3**
  
  - [ ]* 6.7 Write unit tests for evaluation scenarios
    - Test with valid documents (no issues)
    - Test with documents containing code errors
    - Test with documents having coherence issues
    - _Requirements: 3.1, 3.3, 3.4, 3.5_

- [x] 7. Implement file I/O utilities
  - [x] 7.1 Create file I/O functions in vividoc/utils/io.py
    - Implement save_json() to save Pydantic models to JSON files
    - Implement load_json() to load and validate JSON against Pydantic models
    - Add error logging for file operations
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_
  
  - [ ]* 7.2 Write property test for file persistence round-trip
    - **Property 9: File Persistence Round-Trip**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**
  
  - [ ]* 7.3 Write unit tests for file I/O error cases
    - Test missing files, invalid JSON, permission errors
    - Verify error logging includes file paths
    - _Requirements: 9.6_

- [x] 8. Implement pipeline orchestration
  - [x] 8.1 Create RunnerConfig dataclass
    - Define configuration with llm_provider, llm_model, and output_dir
    - Set default values
    - _Requirements: 6.1_
  
  - [x] 8.2 Implement Runner.run() method
    - Accept topic string as input
    - Execute Planner, save DocumentSpec to file
    - Execute Executor, save GeneratedDocument to file
    - Execute Evaluator, save EvaluationFeedback to file
    - Implement feedback loop: if requires_revision, call Executor again with feedback
    - Return final GeneratedDocument when validation passes
    - Add error handling: log and halt on failures
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  
  - [ ]* 8.3 Write unit tests for pipeline execution
    - Test complete pipeline with mock agents
    - Test feedback loop iteration
    - Test error handling and halting
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [ ] 9. Checkpoint - Ensure pipeline tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Implement CLI interface
  - [x] 10.1 Update plan command in vividoc/cli.py
    - Accept topic as required argument
    - Accept optional output path
    - Create PlannerConfig and run Planner
    - Save DocumentSpec to output file
    - _Requirements: 7.1, 7.5_
  
  - [x] 10.2 Update exec command in vividoc/cli.py
    - Accept spec_file path as required argument
    - Accept optional output path
    - Load DocumentSpec from file
    - Create ExecutorConfig and run Executor
    - Save GeneratedDocument to output file
    - _Requirements: 7.2, 7.6_
  
  - [x] 10.3 Update eval command in vividoc/cli.py
    - Accept doc_file path as required argument
    - Accept optional output path
    - Load GeneratedDocument from file
    - Create EvaluatorConfig and run Evaluator
    - Save EvaluationFeedback to output file
    - _Requirements: 7.3, 7.7_
  
  - [x] 10.4 Update run command in vividoc/cli.py
    - Accept topic as required argument
    - Accept optional output_dir
    - Create RunnerConfig and run complete pipeline
    - Save all intermediate outputs to output_dir
    - _Requirements: 7.4, 7.8_
  
  - [ ]* 10.5 Write unit tests for CLI commands
    - Test each command with mock agents
    - Test argument parsing and validation
    - Test file path handling
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_

- [ ] 11. Implement Web UI backend
  - [x] 11.1 Create Flask app in ui/app.py
    - Set up Flask application with routes
    - Add route for spec editor: GET /editor?spec_file=path
    - Add route for saving edited specs: POST /editor/save
    - Add route for document viewer: GET /document?doc_file=path
    - Serve static files (CSS, JS)
    - _Requirements: 8.1_
  
  - [x] 11.2 Implement spec editor backend endpoints
    - Load DocumentSpec from file and return as JSON
    - Accept edited DocumentSpec and save to file
    - Validate against Pydantic model before saving
    - _Requirements: 8.2, 8.5_
  
  - [x] 11.3 Implement document viewer backend endpoint
    - Load GeneratedDocument from file and return as JSON
    - _Requirements: 8.6_

- [ ] 12. Implement Web UI frontend
  - [x] 12.1 Create spec editor HTML template in ui/templates/spec_editor.html
    - Beautiful, modern academic design using Tailwind CSS or similar
    - Display topic at top
    - List all knowledge units with expand/collapse
    - Show id, unit_content, text_description, interaction_description for each unit
    - _Requirements: 8.2, 8.9_
  
  - [x] 12.2 Create spec editor JavaScript in ui/static/js/spec_editor.js
    - Load spec from backend on page load
    - Enable inline editing of text_description and interaction_description fields
    - Add buttons to add new knowledge units
    - Add buttons to remove knowledge units
    - Add drag-and-drop to reorder knowledge units
    - Save button to POST edited spec back to backend
    - _Requirements: 8.3, 8.4, 8.5_
  
  - [x] 12.3 Create document viewer HTML template in ui/templates/document.html
    - Beautiful, modern academic design
    - Display topic as title
    - Render each knowledge unit with text content
    - Include placeholder divs for interactive components
    - _Requirements: 8.6, 8.9_
  
  - [x] 12.4 Create document viewer JavaScript in ui/static/js/runner.js
    - Load generated document from backend on page load
    - Initialize Pyodide for Python execution in browser
    - For each knowledge unit with interactive_code, execute code using Pyodide
    - Render visualizations in placeholder divs
    - Enable user interaction with controls (sliders, buttons, etc.)
    - _Requirements: 8.7, 8.8, 8.10_
  
  - [x] 12.5 Create CSS styling in ui/static/css/style.css
    - Beautiful, modern academic styling
    - Clean typography and spacing
    - Responsive design for different screen sizes
    - Smooth transitions and animations
    - _Requirements: 8.9_

- [ ] 13. Final checkpoint - End-to-end testing
  - [ ] 13.1 Test complete workflow with "What is π?" example
    - Run plan command with topic
    - Open spec editor, make minor edits, save
    - Run exec command with edited spec
    - Run eval command with generated document
    - Open document viewer and verify rendering
    - _Requirements: All_
  
  - [ ] 13.2 Test run command end-to-end
    - Run complete pipeline with a topic
    - Verify all intermediate files are created
    - Open document viewer and verify rendering
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The system uses Python with Pydantic for type safety
- LLM provider and model are configurable (default: Google Gemini)
- Web UI emphasizes beautiful design and human-in-the-loop editing
