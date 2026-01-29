# Requirements Document: Vividoc System

## Introduction

The Vividoc System is an academic research project for generating interactive educational documents. The system uses a three-phase pipeline (Planner, Executor, Evaluator) to transform a topic into a complete interactive document with text explanations and executable code visualizations. The system leverages LLM capabilities through Google Gemini models and uses Pydantic for structured data validation.

## Glossary

- **Vividoc_System**: The complete three-phase pipeline for generating interactive educational documents
- **Planner_Agent**: The first phase that generates document structure with knowledge units
- **Executor_Agent**: The second phase that generates text and interactive code progressively
- **Evaluator_Agent**: The third phase that checks coherence and runtime correctness
- **Knowledge_Unit**: A self-contained unit of educational content with text and interaction descriptions (also called KnowledgeUnitSpec in code)
- **Document_Spec**: The structured JSON output from the Planner containing all knowledge units
- **Interactive_Component**: Executable code that provides visualization or interaction for a knowledge unit
- **LLM_Client**: The interface for calling Google Gemini models
- **Structured_Output**: JSON responses validated against Pydantic schemas

## Requirements

### Requirement 1: Planner Agent Document Structure Generation

**User Story:** As a researcher, I want the Planner Agent to generate a structured document specification from a topic, so that the Executor has a clear plan for content generation.

#### Acceptance Criteria

1. WHEN a topic string is provided as input, THE Planner_Agent SHALL generate a Document_Spec containing knowledge units
2. WHEN generating knowledge units, THE Planner_Agent SHALL create unique identifiers for each unit
3. WHEN creating a knowledge unit, THE Planner_Agent SHALL include unit_content, text_description, and interaction_description fields
4. WHEN generating text_description, THE Planner_Agent SHALL create self-contained descriptions suitable for text generation
5. WHEN generating interaction_description, THE Planner_Agent SHALL create self-contained descriptions suitable for interactive code generation
6. WHEN the Planner_Agent completes processing, THE Planner_Agent SHALL output the Document_Spec in valid JSON format
7. WHEN calling the LLM, THE Planner_Agent SHALL use the configured LLM provider and model from PlannerConfig
8. WHEN requesting structured output, THE Planner_Agent SHALL use Pydantic models with response_json_schema configuration

### Requirement 2: Executor Agent Content Generation

**User Story:** As a researcher, I want the Executor Agent to generate text and interactive code for each knowledge unit, so that the document contains complete educational content.

#### Acceptance Criteria

1. WHEN a Document_Spec is provided as input, THE Executor_Agent SHALL process each knowledge unit sequentially
2. WHEN processing a knowledge unit, THE Executor_Agent SHALL generate text content based on text_description
3. WHEN text content is generated, THE Executor_Agent SHALL generate interactive code based on interaction_description
4. WHEN interactive code is generated, THE Executor_Agent SHALL execute the code to check for bugs
5. WHEN bugs are detected in interactive code, THE Executor_Agent SHALL fix the code and re-validate
6. WHEN all knowledge units are processed, THE Executor_Agent SHALL output a complete document with text and interactive components
7. WHEN calling the LLM, THE Executor_Agent SHALL use the configured LLM provider and model from ExecutorConfig
8. WHEN generating code, THE Executor_Agent SHALL produce executable Python code for visualizations

### Requirement 3: Evaluator Agent Quality Validation

**User Story:** As a researcher, I want the Evaluator Agent to validate document quality, so that generated content meets coherence and correctness standards.

#### Acceptance Criteria

1. WHEN a generated document is provided as input, THE Evaluator_Agent SHALL check overall text fluency and coherence
2. WHEN checking text coherence, THE Evaluator_Agent SHALL validate logical flow between knowledge units
3. WHEN validating interactive components, THE Evaluator_Agent SHALL verify that each component renders correctly
4. WHEN validation issues are found, THE Evaluator_Agent SHALL generate feedback for the Executor_Agent
5. WHEN all checks pass, THE Evaluator_Agent SHALL mark the document as validated
6. WHEN calling the LLM, THE Evaluator_Agent SHALL use the configured LLM provider and model from EvaluatorConfig

### Requirement 4: LLM Integration

**User Story:** As a developer, I want consistent LLM integration across all agents, so that the system uses a unified interface for model calls.

#### Acceptance Criteria

1. WHEN any agent needs to call an LLM, THE LLM_Client SHALL use the provider specified in the agent's configuration
2. WHEN making text generation calls, THE LLM_Client SHALL use the model specified in the agent's configuration
3. WHEN requesting structured output, THE LLM_Client SHALL accept Pydantic model schemas
4. WHEN structured output is requested, THE LLM_Client SHALL configure response_mime_type as application/json
5. WHEN structured output is received, THE LLM_Client SHALL validate responses against Pydantic schemas
6. WHEN validation succeeds, THE LLM_Client SHALL return typed Pydantic model instances

### Requirement 5: Data Models and Validation

**User Story:** As a developer, I want strongly-typed data models, so that data flows between agents are validated and type-safe.

#### Acceptance Criteria

1. THE Vividoc_System SHALL define a KnowledgeUnit Pydantic model with id, unit_content, text_description, and interaction_description fields
2. THE Vividoc_System SHALL define a DocumentSpec Pydantic model with topic and knowledge_units fields
3. THE Vividoc_System SHALL define a GeneratedContent Pydantic model for Executor output
4. THE Vividoc_System SHALL define an EvaluationResult Pydantic model for Evaluator feedback
5. WHEN parsing JSON data, THE Vividoc_System SHALL use Pydantic model_validate_json method
6. WHEN serializing models, THE Vividoc_System SHALL use Pydantic model_dump_json method

### Requirement 6: Pipeline Orchestration

**User Story:** As a researcher, I want to run the complete pipeline end-to-end, so that I can generate interactive documents from topics with a single command.

#### Acceptance Criteria

1. WHEN the run command is invoked with a topic, THE Vividoc_System SHALL execute the Planner_Agent first
2. WHEN the Planner_Agent completes, THE Vividoc_System SHALL pass the Document_Spec to the Executor_Agent
3. WHEN the Executor_Agent completes, THE Vividoc_System SHALL pass the generated document to the Evaluator_Agent
4. WHEN the Evaluator_Agent provides feedback, THE Vividoc_System SHALL pass feedback to the Executor_Agent for refinement
5. WHEN the Evaluator_Agent validates the document, THE Vividoc_System SHALL complete the pipeline
6. WHEN any phase fails, THE Vividoc_System SHALL log the error and halt execution

### Requirement 7: CLI Interface

**User Story:** As a researcher, I want a command-line interface, so that I can run individual phases or the complete pipeline.

#### Acceptance Criteria

1. THE Vividoc_System SHALL provide a plan command that executes only the Planner_Agent
2. THE Vividoc_System SHALL provide an exec command that executes only the Executor_Agent
3. THE Vividoc_System SHALL provide an eval command that executes only the Evaluator_Agent
4. THE Vividoc_System SHALL provide a run command that executes the complete pipeline
5. WHEN the plan command is invoked, THE Vividoc_System SHALL accept a topic as input
6. WHEN the exec command is invoked, THE Vividoc_System SHALL accept a Document_Spec file path as input
7. WHEN the eval command is invoked, THE Vividoc_System SHALL accept a generated document file path as input
8. WHEN the run command is invoked, THE Vividoc_System SHALL accept a topic as input

### Requirement 8: Web UI Display

**User Story:** As a researcher, I want a web interface to view generated documents, so that I can see text and interactive components rendered together.

#### Acceptance Criteria

1. THE Vividoc_System SHALL provide a web interface in the ui/ directory
2. THE Web_UI SHALL provide a spec editor interface for human-in-the-loop editing after Planner generates the spec
3. WHEN viewing a DocumentSpec in the editor, THE Web_UI SHALL allow users to add, remove, or reorder knowledge units
4. WHEN editing a knowledge unit, THE Web_UI SHALL allow users to modify text_description and interaction_description fields
5. WHEN modifications are complete, THE Web_UI SHALL save the edited DocumentSpec back to JSON format
6. WHEN a generated document is loaded, THE Web_UI SHALL display text content for each knowledge unit
7. WHEN displaying a knowledge unit with interactive code, THE Web_UI SHALL render the interactive component
8. WHEN rendering interactive components, THE Web_UI SHALL execute Python code in a browser-compatible environment
9. THE Web_UI SHALL use a beautiful, modern academic style for document presentation
10. WHEN interactive components contain user controls, THE Web_UI SHALL enable user interaction with those controls

### Requirement 9: File I/O and Persistence

**User Story:** As a developer, I want structured file I/O, so that intermediate outputs can be saved and loaded between pipeline phases.

#### Acceptance Criteria

1. WHEN the Planner_Agent completes, THE Vividoc_System SHALL save the Document_Spec to a JSON file
2. WHEN the Executor_Agent completes, THE Vividoc_System SHALL save the generated document to a JSON file
3. WHEN the Evaluator_Agent completes, THE Vividoc_System SHALL save evaluation results to a JSON file
4. WHEN loading a Document_Spec, THE Vividoc_System SHALL validate it against the DocumentSpec Pydantic model
5. WHEN loading a generated document, THE Vividoc_System SHALL validate it against the GeneratedContent Pydantic model
6. WHEN file operations fail, THE Vividoc_System SHALL log the error with the file path

### Requirement 10: Code Execution and Validation

**User Story:** As a researcher, I want interactive code to be validated before inclusion, so that the final document contains only working visualizations.

#### Acceptance Criteria

1. WHEN the Executor_Agent generates interactive code, THE Vividoc_System SHALL execute the code in an isolated environment
2. WHEN code execution succeeds, THE Vividoc_System SHALL capture any runtime output or errors
3. WHEN code execution fails, THE Vividoc_System SHALL extract the error message and stack trace
4. WHEN bugs are detected, THE Executor_Agent SHALL use the error information to generate fixed code
5. WHEN fixed code is generated, THE Vividoc_System SHALL re-execute the code to validate the fix
6. WHEN code validation succeeds after fixes, THE Vividoc_System SHALL include the validated code in the document
