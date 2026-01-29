# Requirements Document: ViviDoc Web UI

## Introduction

The ViviDoc Web UI provides a browser-based interface for generating interactive educational documents. Users can input topics, generate document specifications, edit those specifications, trigger document generation, monitor progress in real-time, and view/download the resulting HTML documents. The system integrates with existing ViviDoc backend components (Planner, Executor, Evaluator) through a RESTful API architecture.

## Glossary

- **System**: The complete ViviDoc Web UI application (frontend + backend)
- **Backend**: The FastAPI RESTful API server
- **Frontend**: The React-based web application
- **Planner**: Existing component that generates document specifications from topics
- **Executor**: Existing component that generates document content from specifications
- **Evaluator**: Existing component that evaluates generated content quality
- **Spec**: Document specification containing knowledge units and metadata
- **KU**: Knowledge Unit - a discrete section of educational content
- **Job**: An asynchronous task (spec generation or document generation)
- **Progress_Monitor**: Component that tracks and reports job execution progress
- **Document_Viewer**: Component that renders generated HTML documents
- **Spec_Editor**: Component that allows users to modify specifications

## Requirements

### Requirement 1: Topic Input and Spec Generation

**User Story:** As a user, I want to input a topic and generate a document specification, so that I can create educational content on any subject.

#### Acceptance Criteria

1. WHEN a user submits a topic string, THE Backend SHALL invoke the Planner to generate a document specification
2. WHEN the Planner completes, THE Backend SHALL return a unique spec identifier and the generated specification
3. WHEN spec generation is in progress, THE Frontend SHALL display a loading indicator
4. WHEN spec generation completes, THE Frontend SHALL display the generated specification in the Spec_Editor
5. IF spec generation fails, THEN THE Backend SHALL return an error message and THE Frontend SHALL display it to the user

### Requirement 2: Spec Editing

**User Story:** As a user, I want to edit the generated specification, so that I can customize the document structure and content before generation.

#### Acceptance Criteria

1. WHEN a user views a specification, THE Spec_Editor SHALL display all knowledge units with their titles, descriptions, and learning objectives
2. WHEN a user clicks edit on a knowledge unit, THE Frontend SHALL display a modal with editable fields for title, description, and learning objectives
3. WHEN a user saves changes to a knowledge unit, THE Backend SHALL update the specification and persist the changes
4. WHEN a user deletes a knowledge unit, THE Backend SHALL remove it from the specification
5. WHEN a user adds a new knowledge unit, THE Backend SHALL insert it into the specification at the specified position
6. WHEN a user reorders knowledge units via drag-and-drop, THE Backend SHALL update the specification with the new order
7. FOR ALL specification modifications, updating then retrieving the specification SHALL return the modified version (round-trip property)

### Requirement 3: Document Generation

**User Story:** As a user, I want to generate an interactive document from my specification, so that I can produce the final educational content.

#### Acceptance Criteria

1. WHEN a user confirms a specification, THE Backend SHALL create a document generation job
2. WHEN a document generation job starts, THE Backend SHALL invoke the Executor with the specification
3. WHEN the Executor completes, THE Backend SHALL invoke the Evaluator to assess content quality
4. WHEN document generation completes successfully, THE Backend SHALL store the generated HTML and return a document identifier
5. IF document generation fails, THEN THE Backend SHALL mark the job as failed and return an error message

### Requirement 4: Real-Time Progress Tracking

**User Story:** As a user, I want to see real-time progress updates during document generation, so that I understand what the system is doing and how long it will take.

#### Acceptance Criteria

1. WHEN a document generation job is running, THE Progress_Monitor SHALL poll the Backend every 2 seconds for status updates
2. WHEN the Backend receives a progress request, THE System SHALL return the current phase (Planning, Executing, Evaluating) and overall percentage
3. WHEN the Executor processes a knowledge unit, THE System SHALL report the KU identifier and current stage (stage1 for text, stage2 for code)
4. WHEN displaying progress, THE Frontend SHALL show overall progress, current phase, and per-KU status
5. WHEN a job completes, THE Progress_Monitor SHALL stop polling and display completion status

### Requirement 5: Document Viewing

**User Story:** As a user, I want to view the generated HTML document in the browser, so that I can review the content before downloading.

#### Acceptance Criteria

1. WHEN a document generation job completes, THE Frontend SHALL retrieve the HTML content from the Backend
2. WHEN displaying HTML content, THE Document_Viewer SHALL render it in an isolated iframe to prevent style conflicts
3. WHEN the HTML contains interactive elements, THE Document_Viewer SHALL preserve their functionality
4. IF the HTML content is malformed, THEN THE Document_Viewer SHALL display an error message

### Requirement 6: Document Download

**User Story:** As a user, I want to download the generated HTML document, so that I can save it locally or share it with others.

#### Acceptance Criteria

1. WHEN a user clicks the download button, THE Backend SHALL serve the HTML file with appropriate headers for download
2. WHEN the download initiates, THE Frontend SHALL trigger a browser download with a descriptive filename
3. THE downloaded file SHALL be a valid standalone HTML document that opens correctly in any modern browser

### Requirement 7: API Endpoints

**User Story:** As a frontend developer, I want well-defined RESTful API endpoints, so that I can integrate the UI with the backend services.

#### Acceptance Criteria

1. THE Backend SHALL expose POST /api/spec/generate endpoint that accepts a topic and returns a spec identifier
2. THE Backend SHALL expose GET /api/spec/{spec_id} endpoint that returns specification details
3. THE Backend SHALL expose PUT /api/spec/{spec_id} endpoint that accepts specification updates
4. THE Backend SHALL expose POST /api/document/generate endpoint that accepts a spec identifier and returns a job identifier
5. THE Backend SHALL expose GET /api/jobs/{job_id}/status endpoint that returns job status and progress information
6. THE Backend SHALL expose GET /api/document/{document_id} endpoint that returns document metadata
7. THE Backend SHALL expose GET /api/document/{document_id}/html endpoint that returns HTML content
8. THE Backend SHALL expose GET /api/document/{document_id}/download endpoint that serves the HTML file for download
9. FOR ALL API endpoints, THE Backend SHALL return appropriate HTTP status codes (200, 400, 404, 500)
10. FOR ALL API endpoints, THE Backend SHALL return JSON responses with consistent error message format

### Requirement 8: Job Management

**User Story:** As a system administrator, I want asynchronous job management, so that long-running tasks don't block the API and users can track progress.

#### Acceptance Criteria

1. WHEN a long-running task is initiated, THE Backend SHALL create a job with a unique identifier
2. WHEN a job is created, THE Backend SHALL execute it in a background thread
3. WHEN a job is executing, THE Backend SHALL maintain its status (running, completed, failed) in memory
4. WHEN the Executor processes content, THE Backend SHALL receive progress callbacks and update job status
5. WHEN a job completes or fails, THE Backend SHALL update the final status and preserve results

### Requirement 9: UI Layout and Components

**User Story:** As a user, I want a clear three-panel layout, so that I can easily navigate between spec editing, document viewing, and progress monitoring.

#### Acceptance Criteria

1. THE Frontend SHALL display a left sidebar containing the topic input and spec editor
2. THE Frontend SHALL display a center panel containing the document viewer
3. THE Frontend SHALL display a right panel containing the progress monitor
4. WHEN the viewport is resized, THE Frontend SHALL maintain readable proportions for all three panels
5. WHEN no document is generated yet, THE Frontend SHALL display a placeholder message in the center panel

### Requirement 10: Integration with Existing Components

**User Story:** As a developer, I want seamless integration with existing ViviDoc components, so that I can reuse proven functionality without reimplementation.

#### Acceptance Criteria

1. THE Backend SHALL import and use vividoc.planner.Planner for spec generation
2. THE Backend SHALL import and use vividoc.executor.Executor for document generation
3. THE Backend SHALL import and use vividoc.evaluator.Evaluator for content evaluation
4. THE Backend SHALL use vividoc.models.DocumentSpec for specification data structures
5. THE Backend SHALL use vividoc.models.GeneratedDocument for document data structures
6. WHEN the Executor is invoked, THE Backend SHALL provide a progress callback function
7. WHEN the progress callback is invoked, THE Backend SHALL update the job status with current progress information
