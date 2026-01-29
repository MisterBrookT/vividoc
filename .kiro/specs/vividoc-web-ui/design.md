# Design Document: ViviDoc Web UI

## Overview

The ViviDoc Web UI is a full-stack web application that provides a browser-based interface for generating interactive educational documents. The system follows a client-server architecture with a React frontend communicating with a FastAPI backend via RESTful APIs. The backend integrates with existing ViviDoc components (Planner, Executor, Evaluator) and manages asynchronous job execution with real-time progress tracking.

The user workflow is linear and intuitive:
1. Enter topic → Generate spec (via Planner)
2. Edit spec → Modify knowledge units
3. Generate document → Execute in background (via Executor + Evaluator)
4. Monitor progress → Real-time updates via polling
5. View/download → Render HTML in browser or save locally

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              React Frontend (Vite)                    │  │
│  │  ┌─────────┐  ┌──────────┐  ┌────────────────┐     │  │
│  │  │  Left   │  │  Center  │  │     Right      │     │  │
│  │  │ Sidebar │  │  Panel   │  │     Panel      │     │  │
│  │  │         │  │          │  │                │     │  │
│  │  │ Topic   │  │ Document │  │   Progress     │     │  │
│  │  │ Input + │  │  Viewer  │  │   Monitor      │     │  │
│  │  │  Spec   │  │ (iframe) │  │                │     │  │
│  │  │ Editor  │  │          │  │                │     │  │
│  │  └─────────┘  └──────────┘  └────────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  API Routes                           │  │
│  │  /api/spec/*  /api/document/*  /api/jobs/*          │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Job Management Layer                     │  │
│  │  - In-memory job storage                             │  │
│  │  - Background thread execution                       │  │
│  │  - Progress callback handling                        │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Integration with ViviDoc Core              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │ Planner  │  │ Executor │  │Evaluator │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- React 18+ with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Axios for HTTP requests
- React DnD for drag-and-drop functionality

**Backend:**
- FastAPI (Python 3.10+)
- Pydantic for data validation
- Threading for background job execution
- Existing ViviDoc components (Planner, Executor, Evaluator)

### Deployment Model

- Local deployment only (single machine)
- No authentication required (single-user mode)
- Frontend served as static files by FastAPI
- Backend and frontend run on same host (e.g., localhost:8000)

## Components and Interfaces

### Backend Components

#### 1. API Router (`api/routes.py`)

Defines all RESTful endpoints and request/response handling.

**Endpoints:**

```python
# Spec Management
POST   /api/spec/generate
  Request: { "topic": str }
  Response: { "spec_id": str, "spec": DocumentSpec }

GET    /api/spec/{spec_id}
  Response: { "spec": DocumentSpec }

PUT    /api/spec/{spec_id}
  Request: { "spec": DocumentSpec }
  Response: { "spec": DocumentSpec }

# Document Generation
POST   /api/document/generate
  Request: { "spec_id": str }
  Response: { "job_id": str }

GET    /api/document/{document_id}
  Response: { "document_id": str, "created_at": str, "spec_id": str }

GET    /api/document/{document_id}/html
  Response: { "html": str }

GET    /api/document/{document_id}/download
  Response: HTML file download

# Job Management
GET    /api/jobs/{job_id}/status
  Response: {
    "job_id": str,
    "status": "running" | "completed" | "failed",
    "progress": {
      "phase": "planning" | "executing" | "evaluating",
      "overall_percent": float,
      "current_ku": str | null,
      "ku_stage": "stage1" | "stage2" | null,
      "ku_progress": [
        {
          "ku_id": str,
          "title": str,
          "status": "pending" | "stage1" | "stage2" | "completed"
        }
      ]
    },
    "result": { "document_id": str } | null,
    "error": str | null
  }
```

#### 2. Job Manager (`services/job_manager.py`)

Manages asynchronous job execution and progress tracking.

```python
class JobManager:
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.lock = threading.Lock()
    
    def create_job(self, job_type: str) -> str:
        """Create a new job and return its ID"""
        
    def start_job(self, job_id: str, target_fn: Callable, *args, **kwargs):
        """Execute job in background thread"""
        
    def update_progress(self, job_id: str, progress: ProgressUpdate):
        """Update job progress (called by callbacks)"""
        
    def get_status(self, job_id: str) -> JobStatus:
        """Get current job status and progress"""
        
    def mark_completed(self, job_id: str, result: Any):
        """Mark job as completed with result"""
        
    def mark_failed(self, job_id: str, error: str):
        """Mark job as failed with error message"""
```

**Job Data Structure:**

```python
@dataclass
class Job:
    job_id: str
    job_type: str  # "spec_generation" | "document_generation"
    status: str  # "running" | "completed" | "failed"
    created_at: datetime
    progress: ProgressInfo
    result: Optional[Any] = None
    error: Optional[str] = None

@dataclass
class ProgressInfo:
    phase: str  # "planning" | "executing" | "evaluating"
    overall_percent: float
    current_ku: Optional[str] = None
    ku_stage: Optional[str] = None  # "stage1" | "stage2"
    ku_progress: List[KUProgress] = field(default_factory=list)

@dataclass
class KUProgress:
    ku_id: str
    title: str
    status: str  # "pending" | "stage1" | "stage2" | "completed"
```

#### 3. Spec Service (`services/spec_service.py`)

Handles spec generation and CRUD operations.

```python
class SpecService:
    def __init__(self, planner: Planner):
        self.planner = planner
        self.specs: Dict[str, DocumentSpec] = {}
    
    def generate_spec(self, topic: str) -> Tuple[str, DocumentSpec]:
        """Generate spec using Planner, return spec_id and spec"""
        
    def get_spec(self, spec_id: str) -> DocumentSpec:
        """Retrieve spec by ID"""
        
    def update_spec(self, spec_id: str, spec: DocumentSpec) -> DocumentSpec:
        """Update existing spec"""
        
    def delete_ku(self, spec_id: str, ku_index: int) -> DocumentSpec:
        """Delete knowledge unit from spec"""
        
    def add_ku(self, spec_id: str, ku: KnowledgeUnit, position: int) -> DocumentSpec:
        """Add knowledge unit to spec at position"""
        
    def reorder_kus(self, spec_id: str, new_order: List[int]) -> DocumentSpec:
        """Reorder knowledge units"""
```

#### 4. Document Service (`services/document_service.py`)

Handles document generation and storage.

```python
class DocumentService:
    def __init__(self, executor: Executor, evaluator: Evaluator, job_manager: JobManager):
        self.executor = executor
        self.evaluator = evaluator
        self.job_manager = job_manager
        self.documents: Dict[str, GeneratedDocument] = {}
    
    def generate_document(self, spec_id: str, spec: DocumentSpec) -> str:
        """Start document generation job, return job_id"""
        
    def _execute_generation(self, job_id: str, spec: DocumentSpec):
        """Background task: execute generation with progress callbacks"""
        
    def _progress_callback(self, job_id: str, phase: str, ku_id: str, stage: str):
        """Callback invoked by Executor to report progress"""
        
    def get_document(self, document_id: str) -> GeneratedDocument:
        """Retrieve generated document"""
        
    def get_html(self, document_id: str) -> str:
        """Get HTML content of document"""
```

#### 5. Executor Extension (`executor_extension.py`)

Extends the existing Executor to support progress callbacks.

```python
class ExecutorWithProgress(Executor):
    def __init__(self, *args, progress_callback: Optional[Callable] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress_callback = progress_callback
    
    def execute(self, spec: DocumentSpec) -> GeneratedDocument:
        """Override to add progress reporting"""
        if self.progress_callback:
            self.progress_callback("executing", None, None)
        
        for ku in spec.knowledge_units:
            # Stage 1: Text generation
            if self.progress_callback:
                self.progress_callback("executing", ku.id, "stage1")
            text_content = self._generate_text(ku)
            
            # Stage 2: Code generation
            if self.progress_callback:
                self.progress_callback("executing", ku.id, "stage2")
            code_content = self._generate_code(ku)
            
            # Mark completed
            if self.progress_callback:
                self.progress_callback("executing", ku.id, "completed")
        
        return super().execute(spec)
```

### Frontend Components

#### 1. App Layout (`App.tsx`)

Main application container with three-panel layout.

```typescript
interface AppProps {}

const App: React.FC<AppProps> = () => {
  const [specId, setSpecId] = useState<string | null>(null);
  const [spec, setSpec] = useState<DocumentSpec | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);
  
  return (
    <div className="flex h-screen">
      <LeftSidebar 
        spec={spec}
        onSpecGenerated={(id, newSpec) => {
          setSpecId(id);
          setSpec(newSpec);
        }}
        onSpecUpdated={(newSpec) => setSpec(newSpec)}
        onGenerateDocument={(jId) => setJobId(jId)}
      />
      <CenterPanel documentId={documentId} />
      <RightPanel 
        jobId={jobId}
        onJobCompleted={(docId) => setDocumentId(docId)}
      />
    </div>
  );
};
```

#### 2. Left Sidebar (`components/LeftSidebar.tsx`)

Contains topic input and spec editor.

```typescript
interface LeftSidebarProps {
  spec: DocumentSpec | null;
  onSpecGenerated: (specId: string, spec: DocumentSpec) => void;
  onSpecUpdated: (spec: DocumentSpec) => void;
  onGenerateDocument: (jobId: string) => void;
}

const LeftSidebar: React.FC<LeftSidebarProps> = ({
  spec,
  onSpecGenerated,
  onSpecUpdated,
  onGenerateDocument
}) => {
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  
  const handleGenerateSpec = async () => {
    setLoading(true);
    const response = await api.post("/api/spec/generate", { topic });
    onSpecGenerated(response.data.spec_id, response.data.spec);
    setLoading(false);
  };
  
  const handleGenerateDocument = async () => {
    const response = await api.post("/api/document/generate", { 
      spec_id: spec.id 
    });
    onGenerateDocument(response.data.job_id);
  };
  
  return (
    <div className="w-1/4 border-r p-4">
      <TopicInput 
        value={topic}
        onChange={setTopic}
        onSubmit={handleGenerateSpec}
        loading={loading}
      />
      {spec && (
        <SpecEditor 
          spec={spec}
          onUpdate={onSpecUpdated}
          onGenerate={handleGenerateDocument}
        />
      )}
    </div>
  );
};
```

#### 3. Spec Editor (`components/SpecEditor.tsx`)

Displays and allows editing of knowledge units.

```typescript
interface SpecEditorProps {
  spec: DocumentSpec;
  onUpdate: (spec: DocumentSpec) => void;
  onGenerate: () => void;
}

const SpecEditor: React.FC<SpecEditorProps> = ({ spec, onUpdate, onGenerate }) => {
  const [editingKU, setEditingKU] = useState<KnowledgeUnit | null>(null);
  
  const handleEditKU = (ku: KnowledgeUnit) => {
    setEditingKU(ku);
  };
  
  const handleSaveKU = async (updatedKU: KnowledgeUnit) => {
    const updatedSpec = { ...spec };
    const index = updatedSpec.knowledge_units.findIndex(ku => ku.id === updatedKU.id);
    updatedSpec.knowledge_units[index] = updatedKU;
    
    const response = await api.put(`/api/spec/${spec.id}`, { spec: updatedSpec });
    onUpdate(response.data.spec);
    setEditingKU(null);
  };
  
  const handleDeleteKU = async (kuId: string) => {
    const updatedSpec = { ...spec };
    updatedSpec.knowledge_units = updatedSpec.knowledge_units.filter(
      ku => ku.id !== kuId
    );
    
    const response = await api.put(`/api/spec/${spec.id}`, { spec: updatedSpec });
    onUpdate(response.data.spec);
  };
  
  const handleReorderKUs = async (newOrder: KnowledgeUnit[]) => {
    const updatedSpec = { ...spec, knowledge_units: newOrder };
    const response = await api.put(`/api/spec/${spec.id}`, { spec: updatedSpec });
    onUpdate(response.data.spec);
  };
  
  return (
    <div className="mt-4">
      <h2 className="text-xl font-bold mb-4">Document Specification</h2>
      <DndContext onDragEnd={handleReorderKUs}>
        {spec.knowledge_units.map((ku) => (
          <KUCard
            key={ku.id}
            ku={ku}
            onEdit={() => handleEditKU(ku)}
            onDelete={() => handleDeleteKU(ku.id)}
          />
        ))}
      </DndContext>
      <button onClick={onGenerate} className="mt-4 btn-primary">
        Generate Document
      </button>
      {editingKU && (
        <KUEditModal
          ku={editingKU}
          onSave={handleSaveKU}
          onClose={() => setEditingKU(null)}
        />
      )}
    </div>
  );
};
```

#### 4. Center Panel (`components/CenterPanel.tsx`)

Displays generated HTML document.

```typescript
interface CenterPanelProps {
  documentId: string | null;
}

const CenterPanel: React.FC<CenterPanelProps> = ({ documentId }) => {
  const [html, setHtml] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    if (documentId) {
      setLoading(true);
      api.get(`/api/document/${documentId}/html`)
        .then(response => {
          setHtml(response.data.html);
          setLoading(false);
        });
    }
  }, [documentId]);
  
  const handleDownload = () => {
    window.open(`/api/document/${documentId}/download`, '_blank');
  };
  
  if (!documentId) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-gray-500">Generate a document to view it here</p>
      </div>
    );
  }
  
  return (
    <div className="flex-1 flex flex-col">
      <div className="p-4 border-b">
        <button onClick={handleDownload} className="btn-secondary">
          Download HTML
        </button>
      </div>
      <div className="flex-1 overflow-auto p-4">
        {loading ? (
          <div>Loading document...</div>
        ) : (
          <iframe
            srcDoc={html}
            className="w-full h-full border-0"
            sandbox="allow-scripts"
          />
        )}
      </div>
    </div>
  );
};
```

#### 5. Right Panel (`components/RightPanel.tsx`)

Displays real-time progress monitoring.

```typescript
interface RightPanelProps {
  jobId: string | null;
  onJobCompleted: (documentId: string) => void;
}

const RightPanel: React.FC<RightPanelProps> = ({ jobId, onJobCompleted }) => {
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  
  useEffect(() => {
    if (!jobId) return;
    
    const pollInterval = setInterval(async () => {
      const response = await api.get(`/api/jobs/${jobId}/status`);
      setJobStatus(response.data);
      
      if (response.data.status === "completed") {
        clearInterval(pollInterval);
        onJobCompleted(response.data.result.document_id);
      } else if (response.data.status === "failed") {
        clearInterval(pollInterval);
      }
    }, 2000);
    
    return () => clearInterval(pollInterval);
  }, [jobId]);
  
  if (!jobId) {
    return (
      <div className="w-1/4 border-l p-4">
        <p className="text-gray-500">No active job</p>
      </div>
    );
  }
  
  return (
    <div className="w-1/4 border-l p-4">
      <h2 className="text-xl font-bold mb-4">Progress</h2>
      {jobStatus && (
        <>
          <ProgressBar percent={jobStatus.progress.overall_percent} />
          <div className="mt-4">
            <p className="font-semibold">Phase: {jobStatus.progress.phase}</p>
            <p className="text-sm text-gray-600">
              Status: {jobStatus.status}
            </p>
          </div>
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Knowledge Units</h3>
            {jobStatus.progress.ku_progress.map((ku) => (
              <KUProgressCard key={ku.ku_id} ku={ku} />
            ))}
          </div>
          {jobStatus.error && (
            <div className="mt-4 p-2 bg-red-100 text-red-700 rounded">
              Error: {jobStatus.error}
            </div>
          )}
        </>
      )}
    </div>
  );
};
```

## Data Models

### Backend Models

All models use existing ViviDoc data structures where possible.

```python
# Reuse from vividoc.models
from vividoc.models import (
    DocumentSpec,
    KnowledgeUnit,
    GeneratedDocument,
    LearningObjective
)

# New models for API
class SpecGenerateRequest(BaseModel):
    topic: str

class SpecGenerateResponse(BaseModel):
    spec_id: str
    spec: DocumentSpec

class SpecUpdateRequest(BaseModel):
    spec: DocumentSpec

class DocumentGenerateRequest(BaseModel):
    spec_id: str

class DocumentGenerateResponse(BaseModel):
    job_id: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: ProgressInfo
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

### Frontend Models

```typescript
interface DocumentSpec {
  id: string;
  topic: string;
  knowledge_units: KnowledgeUnit[];
  metadata: SpecMetadata;
}

interface KnowledgeUnit {
  id: string;
  title: string;
  description: string;
  learning_objectives: string[];
  prerequisites: string[];
}

interface SpecMetadata {
  created_at: string;
  updated_at: string;
}

interface JobStatus {
  job_id: string;
  status: "running" | "completed" | "failed";
  progress: ProgressInfo;
  result?: { document_id: string };
  error?: string;
}

interface ProgressInfo {
  phase: "planning" | "executing" | "evaluating";
  overall_percent: number;
  current_ku?: string;
  ku_stage?: "stage1" | "stage2";
  ku_progress: KUProgress[];
}

interface KUProgress {
  ku_id: string;
  title: string;
  status: "pending" | "stage1" | "stage2" | "completed";
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Spec Generation Returns Valid Response

*For any* valid topic string, generating a spec should return both a unique spec identifier and a DocumentSpec object.

**Validates: Requirements 1.1, 1.2**

### Property 2: Spec Modification Round-Trip

*For any* specification and any valid modification (add, edit, delete, reorder KU), updating the spec then retrieving it should return the modified version.

**Validates: Requirements 2.3, 2.4, 2.5, 2.6, 2.7**

### Property 3: KU Deletion Removes Target

*For any* specification with N knowledge units, deleting a specific KU should result in a specification with N-1 knowledge units that does not contain the deleted KU.

**Validates: Requirements 2.4**

### Property 4: KU Addition Preserves Position

*For any* specification and any valid position index, adding a new KU at that position should result in the KU appearing at exactly that index in the updated specification.

**Validates: Requirements 2.5**

### Property 5: KU Reordering Preserves Content

*For any* specification, reordering knowledge units should preserve all KU content (titles, descriptions, objectives) while changing only their sequence.

**Validates: Requirements 2.6**

### Property 6: Document Generation Creates Job

*For any* valid specification, initiating document generation should create a job with a unique identifier and status "running".

**Validates: Requirements 3.1**

### Property 7: Generation Workflow Sequence

*For any* document generation job, the execution sequence should be: Planner (if needed) → Executor → Evaluator, with each component receiving the correct inputs.

**Validates: Requirements 3.2, 3.3**

### Property 8: Successful Generation Returns Document

*For any* successful document generation, the system should store the HTML content and return a document identifier that can be used to retrieve that content.

**Validates: Requirements 3.4**

### Property 9: Progress Updates Include Required Fields

*For any* running job, querying its status should return an object containing job_id, status, phase, overall_percent, and ku_progress array.

**Validates: Requirements 4.2, 4.3**

### Property 10: KU Progress Tracking

*For any* knowledge unit being processed, the progress information should report the KU identifier and current stage (stage1, stage2, or completed).

**Validates: Requirements 4.3**

### Property 11: HTML Content Retrieval

*For any* completed document generation job, retrieving the HTML content should return the same HTML that was generated by the Executor.

**Validates: Requirements 5.1**

### Property 12: Downloaded HTML is Valid

*For any* generated document, the downloaded HTML file should be a valid, standalone HTML document that can be opened in a browser without external dependencies.

**Validates: Requirements 6.3**

### Property 13: API Endpoint Contracts

*For any* API endpoint, sending a request with valid parameters should return a response matching the specified schema with appropriate HTTP status code (200 for success).

**Validates: Requirements 7.1-7.10**

### Property 14: Job Status Persistence

*For any* job (running, completed, or failed), querying its status multiple times should return consistent information until the job state changes.

**Validates: Requirements 8.3, 8.5**

### Property 15: Progress Callback Integration

*For any* document generation job, when the Executor invokes the progress callback, the job status should be updated to reflect the current phase and KU progress.

**Validates: Requirements 8.4, 10.6, 10.7**

## Error Handling

### Backend Error Handling

**API Level:**
- All endpoints wrapped in try-except blocks
- Return appropriate HTTP status codes:
  - 400 Bad Request: Invalid input parameters
  - 404 Not Found: Resource (spec, document, job) not found
  - 500 Internal Server Error: Unexpected errors
- Consistent error response format:
  ```json
  {
    "error": "Error message",
    "detail": "Detailed error information"
  }
  ```

**Job Execution:**
- Catch exceptions during Planner/Executor/Evaluator execution
- Mark job as "failed" with error message
- Preserve error information for debugging
- Log errors to backend logs

**Resource Management:**
- Validate spec_id, job_id, document_id before operations
- Return 404 if resource not found
- Prevent operations on invalid or non-existent resources

### Frontend Error Handling

**API Errors:**
- Display user-friendly error messages in UI
- Show toast notifications for transient errors
- Display inline errors for form validation
- Provide retry mechanisms for failed operations

**Progress Monitoring:**
- Handle polling failures gracefully
- Display error state if job fails
- Show error message from backend
- Allow user to dismiss error and start new generation

**Document Viewing:**
- Handle malformed HTML gracefully
- Display error message if HTML cannot be rendered
- Provide fallback UI if iframe fails to load

## Testing Strategy

### Dual Testing Approach

The system will use both unit tests and property-based tests to ensure comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs

Both testing approaches are complementary and necessary. Unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across a wide range of inputs.

### Backend Testing

**Unit Tests:**
- Test specific API endpoints with known inputs/outputs
- Test error handling with invalid inputs
- Test job state transitions
- Test integration with Planner/Executor/Evaluator
- Test edge cases (empty specs, single KU, many KUs)

**Property-Based Tests:**
- Use Hypothesis (Python) for property-based testing
- Minimum 100 iterations per property test
- Each test tagged with: **Feature: vividoc-web-ui, Property N: [property text]**

**Property Test Examples:**
```python
# Property 2: Spec Modification Round-Trip
@given(spec=document_spec_strategy(), modification=modification_strategy())
def test_spec_modification_roundtrip(spec, modification):
    """Feature: vividoc-web-ui, Property 2: Spec modification round-trip"""
    # Apply modification
    spec_id = spec_service.create_spec(spec)
    modified_spec = apply_modification(spec, modification)
    spec_service.update_spec(spec_id, modified_spec)
    
    # Retrieve and verify
    retrieved_spec = spec_service.get_spec(spec_id)
    assert retrieved_spec == modified_spec

# Property 9: Progress Updates Include Required Fields
@given(job_type=sampled_from(["spec_generation", "document_generation"]))
def test_progress_updates_structure(job_type):
    """Feature: vividoc-web-ui, Property 9: Progress updates include required fields"""
    job_id = job_manager.create_job(job_type)
    status = job_manager.get_status(job_id)
    
    assert "job_id" in status
    assert "status" in status
    assert "progress" in status
    assert "phase" in status["progress"]
    assert "overall_percent" in status["progress"]
    assert "ku_progress" in status["progress"]
```

### Frontend Testing

**Unit Tests:**
- Test component rendering with specific props
- Test user interactions (button clicks, form submissions)
- Test API integration with mocked responses
- Test error display and handling
- Use React Testing Library + Jest

**Property-Based Tests:**
- Use fast-check (TypeScript) for property-based testing
- Minimum 100 iterations per property test
- Each test tagged with: **Feature: vividoc-web-ui, Property N: [property text]**

**Property Test Examples:**
```typescript
// Property 4: KU Addition Preserves Position
fc.assert(
  fc.property(
    fc.array(kuGenerator()),
    fc.integer({ min: 0, max: 10 }),
    kuGenerator(),
    (kus, position, newKU) => {
      // Feature: vividoc-web-ui, Property 4: KU addition preserves position
      const spec = { id: "test", knowledge_units: kus };
      const validPosition = Math.min(position, kus.length);
      
      const updatedSpec = addKUAtPosition(spec, newKU, validPosition);
      
      expect(updatedSpec.knowledge_units[validPosition]).toEqual(newKU);
    }
  ),
  { numRuns: 100 }
);
```

### Integration Testing

**End-to-End Workflow:**
- Test complete user workflow: topic → spec → edit → generate → view
- Use Playwright or Cypress for E2E tests
- Test with real backend (not mocked)
- Verify progress updates during generation
- Verify HTML rendering and download

**API Integration:**
- Test all API endpoints with real requests
- Test concurrent requests (if applicable)
- Test job lifecycle (create → running → completed)
- Test error scenarios (invalid IDs, missing resources)

### Test Configuration

**Property-Based Test Settings:**
- Minimum 100 iterations per test (due to randomization)
- Seed tests for reproducibility
- Generate edge cases (empty arrays, boundary values)
- Use shrinking to find minimal failing examples

**Coverage Goals:**
- Backend: 80%+ code coverage
- Frontend: 70%+ code coverage
- All correctness properties implemented as tests
- All error paths tested

## Implementation Notes

### Phase 1: Backend Foundation
1. Set up FastAPI project structure
2. Implement job manager with in-memory storage
3. Create API routes with request/response models
4. Integrate with existing Planner/Executor/Evaluator
5. Extend Executor with progress callbacks
6. Implement spec and document services

### Phase 2: Frontend Foundation
1. Set up React + Vite + TypeScript project
2. Implement three-panel layout
3. Create basic components (TopicInput, SpecEditor, DocumentViewer, ProgressMonitor)
4. Set up API client with Axios
5. Implement state management

### Phase 3: Core Features
1. Implement spec generation workflow
2. Implement spec editing (add, edit, delete, reorder)
3. Implement document generation with job tracking
4. Implement progress polling and display
5. Implement document viewing in iframe
6. Implement document download

### Phase 4: Polish and Testing
1. Add error handling throughout
2. Improve UI/UX (loading states, transitions, feedback)
3. Write unit tests for backend
4. Write property-based tests for backend
5. Write unit tests for frontend
6. Write property-based tests for frontend
7. Perform E2E testing

### Deployment Considerations

**Local Development:**
- Backend runs on localhost:8000
- Frontend dev server proxies API requests to backend
- Hot reload for both frontend and backend

**Production Build:**
- Frontend built as static files
- FastAPI serves static files at root
- API routes under /api prefix
- Single server deployment (backend serves everything)

### Future Enhancements (Out of Scope for MVP)

- Database persistence (replace in-memory storage)
- Multi-user support with authentication
- Vibe mode (conversational document generation)
- Chat history and session management
- WebSocket for real-time progress (replace polling)
- Document versioning and history
- Collaborative editing
- Export to multiple formats (PDF, Markdown)
