import { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import type { DocumentSpec } from './types/models';
import LeftSidebar from './components/LeftSidebar';
import MiddleSpecPanel from './components/MiddleSpecPanel';
import CenterPanel from './components/CenterPanel';
import { getSpec, getSpecHtml } from './api/services';

import './App.css';

function App() {
  const [spec, setSpec] = useState<DocumentSpec | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [liveHtml, setLiveHtml] = useState<string | null>(null);
  const [configModalOpen, setConfigModalOpen] = useState(true);
  const [middlePanelCollapsed, setMiddlePanelCollapsed] = useState(false);

  // When a new spec is generated (from Sidebar input)
  const handleSpecGenerated = (id: string, newSpec: DocumentSpec) => {
    console.log('Spec generated with ID:', id);
    setSpec({ ...newSpec, id }); // Ensure ID is part of spec object if not already
    setDocumentId(null);
    setJobId(null);
    setLiveHtml(null);
    setMiddlePanelCollapsed(false); // Auto-expand when new spec is created
  };

  const handleSpecUpdated = (newSpec: DocumentSpec) => {
    setSpec(newSpec);
  };

  const handleGenerateDocument = (jId: string) => {
    setJobId(jId);
    setDocumentId(null);
    setLiveHtml(null);
    // Optionally collapse middle panel or keep it open? Let's keep it open for now
  };

  const handleJobCompleted = (docId: string) => {
    setDocumentId(docId);
  };

  const handleLiveHtmlUpdate = (html: string | null) => {
    setLiveHtml(html);
  };

  const handleSelectHistory = async (specId: string) => {
    try {
      // Fetch spec
      const specData = await getSpec(specId);
      setSpec(specData.spec);

      // Reset document state
      setDocumentId(null);
      setJobId(null);
      setLiveHtml(null);
      setMiddlePanelCollapsed(false);

      // Try to fetch associated HTML if exists
      const htmlContent = await getSpecHtml(specId);
      if (htmlContent) {
        setLiveHtml(htmlContent);
      }

    } catch (error) {
      console.error("Failed to load history item", error);
    }
  };

  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#18181b',
            color: '#fafafa',
            border: '1px solid #27272a',
            borderRadius: '8px',
            fontSize: '14px',
          },
          success: {
            iconTheme: {
              primary: '#22c55e',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />

      <div className="flex h-screen bg-[var(--bg-app)] selection:bg-indigo-500/30 selection:text-indigo-200 overflow-hidden relative">
        {/* Ambient background effects */}
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-900/10 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-violet-900/10 rounded-full blur-[100px] pointer-events-none" />

        <LeftSidebar
          onSpecGenerated={handleSpecGenerated}
          onSelectHistory={handleSelectHistory}
          configModalOpen={configModalOpen}
          onConfigModalChange={setConfigModalOpen}
          currentSpecId={spec?.id || null}
        />

        <MiddleSpecPanel
          spec={spec}
          onSpecUpdated={handleSpecUpdated}
          onGenerateDocument={handleGenerateDocument}
          collapsed={middlePanelCollapsed}
          onToggleCollapse={() => setMiddlePanelCollapsed(!middlePanelCollapsed)}
        />

        <CenterPanel
          documentId={documentId}
          liveHtml={liveHtml}
          jobId={jobId}
          onJobCompleted={handleJobCompleted}
          onLiveHtmlUpdate={handleLiveHtmlUpdate}
        />

      </div>
    </>
  );
}

export default App;
