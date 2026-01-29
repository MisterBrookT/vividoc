# Implementation Plan: ViviDoc Web UI

## Overview

This implementation plan breaks down the ViviDoc Web UI feature into discrete coding tasks. The approach follows a backend-first strategy, building the API foundation before implementing the frontend. Each task builds incrementally, with testing integrated throughout to catch errors early.

## Tasks

- [x] 1. Set up backend project structure and core models
  - Create FastAPI project with proper directory structure (api/, services/, models/)
  - Define Pydantic models for API requests/responses (SpecGenerateRequest, DocumentGenerateResponse, JobStatusResponse, etc.)
  - Set up CORS middleware for local development
  - Create main.py with FastAPI app initialization
  - _Requirements: 7.1-7.10, 10.1-10.5_

- [ ] 2. Implement job management system
  - [x] 2.1 Create Job and ProgressInfo data classes
    - Implement Job, ProgressInfo, KUProgress dataclasses with proper typing
    - Include job_id, status, progress tracking fields
    - _Requirements: 8.1, 8.3_
  
  - [x] 2.2 Implement JobManager class
    - Create JobManager with in-memory storage (dict)
    - Implement create_job, start_job, update_progress, get_status methods
    - Add thread-safe operations using threading.Lock
    - Implement mark_completed and mark_failed methods
    - _Requirements: 8.1, 8.2, 8.3, 8.5_
  
  - [ ]* 2.3 Write property test for job status persistence
    - **Property 14: Job Status Persistence**
    - **Validates: Requirements 8.3, 8.5**
  
  - [ ]* 2.4 Write unit tests for JobManager
    - Test job creation with unique IDs
    - Test status transitions (running → completed/failed)
    - Test concurrent access with threading
    - _Requirements: 8.1, 8.2, 8.3_

- [ ] 3. Implement spec service
  - [x] 3.1 Create SpecService class
    - Implement generate_spec method using existing Planner
    - Implement get_spec, update_spec methods with in-memory storage
    - Implement delete_ku, add_ku, reorder_kus helper methods
    - Generate unique spec IDs using uuid
    - _Requirements: 1.1, 1.2, 2.3, 2.4, 2.5, 2.6_
  
  - [ ]* 3.2 Write property test for spec generation
    - **Property 1: Spec Generation Returns Valid Response**
    - **Validates: Requirements 1.1, 1.2**
  
  - [ ]* 3.3 Write property test for spec modification round-trip
    - **Property 2: Spec Modification Round-Trip**
    - **Validates: Requirements 2.3, 2.4, 2.5, 2.6, 2.7**
  
  - [ ]* 3.4 Write property test for KU deletion
    - **Property 3: KU Deletion Removes Target**
    - **Validates: Requirements 2.4**
  
  - [ ]* 3.5 Write property test for KU addition position
    - **Property 4: KU Addition Preserves Position**
    - **Validates: Requirements 2.5**
  
  - [ ]* 3.6 Write property test for KU reordering
    - **Property 5: KU Reordering Preserves Content**
    - **Validates: Requirements 2.6**

- [ ] 4. Extend Executor with progress callbacks
  - [x] 4.1 Create ExecutorWithProgress wrapper class
    - Extend or wrap existing Executor class
    - Add progress_callback parameter to constructor
    - Override execute method to invoke callbacks at key points
    - Report phase transitions (planning → executing → evaluating)
    - Report KU-level progress (stage1, stage2, completed)
    - _Requirements: 10.6, 10.7, 4.3_
  
  - [ ]* 4.2 Write property test for progress callback integration
    - **Property 15: Progress Callback Integration**
    - **Validates: Requirements 8.4, 10.6, 10.7**
  
  - [ ]* 4.3 Write unit tests for ExecutorWithProgress
    - Test callback invocation at each phase
    - Test KU-level progress reporting
    - Test execution without callback (callback=None)
    - _Requirements: 10.6, 10.7_

- [ ] 5. Implement document service
  - [x] 5.1 Create DocumentService class
    - Implement generate_document method that creates job and starts background execution
    - Implement _execute_generation background task
    - Implement _progress_callback that updates job status via JobManager
    - Implement get_document and get_html methods with in-memory storage
    - Integrate with ExecutorWithProgress and Evaluator
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.3, 8.4_
  
  - [ ]* 5.2 Write property test for document generation job creation
    - **Property 6: Document Generation Creates Job**
    - **Validates: Requirements 3.1**
  
  - [ ]* 5.3 Write property test for generation workflow sequence
    - **Property 7: Generation Workflow Sequence**
    - **Validates: Requirements 3.2, 3.3**
  
  - [ ]* 5.4 Write property test for successful generation
    - **Property 8: Successful Generation Returns Document**
    - **Validates: Requirements 3.4**
  
  - [ ]* 5.5 Write unit tests for DocumentService
    - Test job creation and background execution
    - Test progress callback updates
    - Test error handling and job failure
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 6. Checkpoint - Ensure backend core tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement API routes
  - [x] 7.1 Create spec management endpoints
    - Implement POST /api/spec/generate endpoint
    - Implement GET /api/spec/{spec_id} endpoint
    - Implement PUT /api/spec/{spec_id} endpoint
    - Add request validation and error handling
    - Return appropriate HTTP status codes (200, 400, 404, 500)
    - _Requirements: 7.1, 7.2, 7.3, 7.9, 7.10_
  
  - [x] 7.2 Create document generation endpoints
    - Implement POST /api/document/generate endpoint
    - Implement GET /api/document/{document_id} endpoint
    - Implement GET /api/document/{document_id}/html endpoint
    - Implement GET /api/document/{document_id}/download endpoint with proper headers
    - _Requirements: 7.4, 7.6, 7.7, 7.8, 6.1_
  
  - [x] 7.3 Create job status endpoint
    - Implement GET /api/jobs/{job_id}/status endpoint
    - Return job status with progress information
    - _Requirements: 7.5, 4.2_
  
  - [ ]* 7.4 Write property test for API endpoint contracts
    - **Property 13: API Endpoint Contracts**
    - **Validates: Requirements 7.1-7.10**
  
  - [ ]* 7.5 Write unit tests for API routes
    - Test each endpoint with valid inputs
    - Test error cases (404, 400, 500)
    - Test response format consistency
    - _Requirements: 7.1-7.10_

- [x] 8. Set up frontend project structure
  - Create React + Vite + TypeScript project
  - Install dependencies (axios, tailwindcss, react-dnd, etc.)
  - Configure Tailwind CSS
  - Set up API client with Axios (base URL configuration)
  - Create TypeScript interfaces for data models (DocumentSpec, KnowledgeUnit, JobStatus, etc.)
  - _Requirements: 9.1-9.5_

- [ ] 9. Implement three-panel layout
  - [x] 9.1 Create App component with layout
    - Implement three-panel flex layout (left sidebar, center panel, right panel)
    - Add state management for spec, jobId, documentId
    - Wire up callbacks between panels
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [ ]* 9.2 Write unit tests for App layout
    - Test panel rendering
    - Test state updates and prop passing
    - _Requirements: 9.1, 9.2, 9.3_

- [ ] 10. Implement left sidebar components
  - [x] 10.1 Create TopicInput component
    - Implement input field and submit button
    - Add loading state during spec generation
    - Handle form submission
    - _Requirements: 1.3_
  
  - [x] 10.2 Create SpecEditor component
    - Display spec metadata and KU list
    - Implement drag-and-drop reordering with react-dnd
    - Add "Generate Document" button
    - _Requirements: 2.1, 2.6_
  
  - [x] 10.3 Create KUCard component
    - Display KU title, description, learning objectives
    - Add edit and delete buttons
    - _Requirements: 2.1_
  
  - [x] 10.4 Create KUEditModal component
    - Implement modal with form fields (title, description, objectives)
    - Add save and cancel buttons
    - Handle form validation
    - _Requirements: 2.2, 2.3_
  
  - [x] 10.5 Implement LeftSidebar component
    - Integrate TopicInput and SpecEditor
    - Handle spec generation API call
    - Handle spec update API calls (edit, delete, reorder)
    - Handle document generation API call
    - Display error messages
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.2, 2.3, 2.4, 2.6, 3.1_
  
  - [ ]* 10.6 Write unit tests for left sidebar components
    - Test TopicInput submission and loading state
    - Test SpecEditor rendering and interactions
    - Test KUCard display and button clicks
    - Test KUEditModal form handling
    - _Requirements: 1.3, 2.1, 2.2_

- [ ] 11. Implement center panel components
  - [x] 11.1 Create DocumentViewer component
    - Implement iframe rendering with srcDoc
    - Add sandbox attribute for security
    - Handle loading state
    - Display placeholder when no document
    - Handle malformed HTML errors
    - _Requirements: 5.2, 5.3, 5.4, 9.5_
  
  - [x] 11.2 Create CenterPanel component
    - Integrate DocumentViewer
    - Fetch HTML content when documentId changes
    - Add download button
    - Handle download click (open download endpoint in new tab)
    - _Requirements: 5.1, 6.2_
  
  - [ ]* 11.3 Write property test for HTML content retrieval
    - **Property 11: HTML Content Retrieval**
    - **Validates: Requirements 5.1**
  
  - [ ]* 11.4 Write unit tests for center panel components
    - Test DocumentViewer rendering with HTML
    - Test placeholder display
    - Test error handling for malformed HTML
    - Test download button functionality
    - _Requirements: 5.1, 5.2, 5.4, 6.2, 9.5_

- [ ] 12. Implement right panel components
  - [x] 12.1 Create ProgressBar component
    - Display progress percentage with visual bar
    - Style with Tailwind CSS
    - _Requirements: 4.4_
  
  - [x] 12.2 Create KUProgressCard component
    - Display KU title and status badge
    - Show different colors for pending/stage1/stage2/completed
    - _Requirements: 4.3, 4.4_
  
  - [x] 12.3 Create ProgressMonitor component
    - Display overall progress bar
    - Display current phase and status
    - Display list of KU progress cards
    - Display error message if job fails
    - _Requirements: 4.4, 4.5_
  
  - [x] 12.4 Create RightPanel component
    - Integrate ProgressMonitor
    - Implement polling mechanism (every 2 seconds)
    - Stop polling when job completes or fails
    - Handle polling errors gracefully
    - Invoke onJobCompleted callback when done
    - _Requirements: 4.1, 4.2, 4.4, 4.5_
  
  - [ ]* 12.5 Write property test for progress updates structure
    - **Property 9: Progress Updates Include Required Fields**
    - **Validates: Requirements 4.2, 4.3**
  
  - [ ]* 12.6 Write property test for KU progress tracking
    - **Property 10: KU Progress Tracking**
    - **Validates: Requirements 4.3**
  
  - [ ]* 12.7 Write unit tests for right panel components
    - Test ProgressBar rendering with different percentages
    - Test KUProgressCard status display
    - Test ProgressMonitor rendering
    - Test RightPanel polling behavior
    - Test polling termination on completion
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 13. Checkpoint - Ensure frontend core tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Integration and end-to-end testing
  - [x] 14.1 Wire all components together
    - Ensure state flows correctly between panels
    - Test complete workflow: topic → spec → edit → generate → view
    - Verify error handling throughout
    - _Requirements: All_
  
  - [ ]* 14.2 Write E2E test for complete workflow
    - Use Playwright or Cypress
    - Test: enter topic → generate spec → edit KU → generate document → view HTML → download
    - Verify progress updates during generation
    - _Requirements: 1.1-6.3_
  
  - [ ]* 14.3 Write property test for downloaded HTML validity
    - **Property 12: Downloaded HTML is Valid**
    - **Validates: Requirements 6.3**

- [ ] 15. Polish and error handling
  - [x] 15.1 Add comprehensive error handling
    - Add try-catch blocks in all API calls
    - Display user-friendly error messages
    - Add toast notifications for transient errors
    - Add inline error displays for forms
    - _Requirements: 1.5, 3.5_
  
  - [x] 15.2 Improve UI/UX
    - Add loading spinners and skeleton screens
    - Add smooth transitions between states
    - Improve responsive layout for different screen sizes
    - Add tooltips and help text
    - Polish styling with Tailwind CSS
    - _Requirements: 9.4_
  
  - [x] 15.3 Add backend logging and error handling
    - Add structured logging throughout backend
    - Ensure all exceptions are caught and logged
    - Return consistent error response format
    - _Requirements: 7.10_

- [x] 16. Final checkpoint - Complete system test
  - Run all unit tests (backend and frontend)
  - Run all property-based tests (backend and frontend)
  - Run E2E tests
  - Test complete workflow manually
  - Verify all requirements are met
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples, edge cases, and error conditions
- Backend uses Python + FastAPI + Hypothesis for property testing
- Frontend uses TypeScript + React + fast-check for property testing
- Integration tests verify the complete system works end-to-end
