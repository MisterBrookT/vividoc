import { useState } from 'react';
import type { DocumentSpec } from './types/models';
import LeftSidebar from './components/LeftSidebar';
import CenterPanel from './components/CenterPanel';
import RightPanel from './components/RightPanel';
import './App.css';

/**
 * Main application component with three-panel layout
 * 
 * Layout structure:
 * - Left Sidebar (25%): Topic input and spec editor
 * - Center Panel (50%): Document viewer
 * - Right Panel (25%): Progress monitor
 * 
 * State management:
 * - specId: Unique identifier for the generated spec
 * - spec: The document specification object
 * - jobId: Unique identifier for the document generation job
 * - documentId: Unique identifier for the generated document
 */
function App() {
  // State for spec management
  const [spec, setSpec] = useState<DocumentSpec | null>(null);
  
  // State for job and document management
  const [jobId, setJobId] = useState<string | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);

  /**
   * Callback invoked when a new spec is generated
   * @param id - The unique spec identifier
   * @param newSpec - The generated specification
   */
  const handleSpecGenerated = (id: string, newSpec: DocumentSpec) => {
    console.log('Spec generated with ID:', id);
    setSpec(newSpec);
    // Reset document state when new spec is generated
    setDocumentId(null);
    setJobId(null);
  };

  /**
   * Callback invoked when the spec is updated (edited)
   * @param newSpec - The updated specification
   */
  const handleSpecUpdated = (newSpec: DocumentSpec) => {
    setSpec(newSpec);
  };

  /**
   * Callback invoked when document generation starts
   * @param jId - The unique job identifier
   */
  const handleGenerateDocument = (jId: string) => {
    setJobId(jId);
    // Clear previous document when starting new generation
    setDocumentId(null);
  };

  /**
   * Callback invoked when document generation completes
   * @param docId - The unique document identifier
   */
  const handleJobCompleted = (docId: string) => {
    setDocumentId(docId);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Sidebar - Topic Input & Spec Editor */}
      <LeftSidebar
        spec={spec}
        onSpecGenerated={handleSpecGenerated}
        onSpecUpdated={handleSpecUpdated}
        onGenerateDocument={handleGenerateDocument}
      />

      {/* Center Panel - Document Viewer */}
      <CenterPanel documentId={documentId} />

      {/* Right Panel - Progress Monitor */}
      <RightPanel
        jobId={jobId}
        onJobCompleted={handleJobCompleted}
      />
    </div>
  );
}

export default App;
