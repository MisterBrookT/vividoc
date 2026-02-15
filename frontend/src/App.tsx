import { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import type { DocumentSpec } from './types/models';
import LeftSidebar from './components/LeftSidebar';
import MiddleSpecPanel from './components/MiddleSpecPanel';
import CenterPanel from './components/CenterPanel';
import RightChatPanel from './components/RightChatPanel';
import { getSpec, getSpecHtml } from './api/services';
import { useJobPolling } from './hooks/useJobPolling';

import './App.css';

function App() {
  const [spec, setSpec] = useState<DocumentSpec | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [liveHtml, setLiveHtml] = useState<string | null>(null);
  const [configModalOpen, setConfigModalOpen] = useState(true);
  const [middlePanelCollapsed, setMiddlePanelCollapsed] = useState(true);
  const [isSpecGenerating, setIsSpecGenerating] = useState(false);

  // Use the polling hook
  const { jobStatus, liveHtml: polledHtml } = useJobPolling(
    jobId,
    (docId) => setDocumentId(docId), // onJobCompleted
    (html) => setLiveHtml(html)      // onLiveHtmlUpdate
  );

  // Spec Generation Handlers
  const handleSpecGenerationStart = () => {
    setIsSpecGenerating(true);
  };

  const handleSpecGenerated = (id: string, newSpec: DocumentSpec) => {
    console.log('Spec generated with ID:', id);
    setSpec({ ...newSpec, id });
    setDocumentId(null);
    setJobId(null);
    setLiveHtml(null);
    setIsSpecGenerating(false);
  };

  const handleSpecUpdated = (newSpec: DocumentSpec) => {
    setSpec(newSpec);
  };

  const handleGenerateDocument = (jId: string) => {
    setJobId(jId);
    setDocumentId(null);
    setLiveHtml(null);
  };

  const handleSelectHistory = async (specId: string) => {
    try {
      const specData = await getSpec(specId);
      setSpec(specData.spec);
      setDocumentId(null);
      setJobId(null);
      setLiveHtml(null);

      const htmlContent = await getSpecHtml(specId);
      if (htmlContent) {
        setLiveHtml(htmlContent);
      }
    } catch (error) {
      console.error("Failed to load history item", error);
    }
  };

  const handleSendMessage = (message: string) => {
    // TODO: Implement chat logic with backend
    console.log("User message:", message);
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

      <div className="fixed inset-0 bg-[var(--bg-app)] selection:bg-indigo-500/30 selection:text-indigo-200 overflow-hidden flex">
        {/* Ambient background effects */}
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-900/10 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-violet-900/10 rounded-full blur-[100px] pointer-events-none" />

        <LeftSidebar
          onSpecGenerated={handleSpecGenerated}
          onSpecGenerationStart={handleSpecGenerationStart}
          onSelectHistory={handleSelectHistory}
          configModalOpen={configModalOpen}
          onConfigModalChange={setConfigModalOpen}
          currentSpecId={spec?.id || null}
          onToggleSpec={() => setMiddlePanelCollapsed(!middlePanelCollapsed)}
          specPanelCollapsed={middlePanelCollapsed}
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
          liveHtml={polledHtml || liveHtml}
          jobStatus={jobStatus}
          spec={spec}
          onViewSpec={() => setMiddlePanelCollapsed(false)}
        />

        <RightChatPanel
          jobStatus={jobStatus}
          onSendMessage={handleSendMessage}
          isGeneratingSpec={isSpecGenerating}
          spec={spec}
          onViewSpec={() => setMiddlePanelCollapsed(false)}
        />

      </div>
    </>
  );
}

export default App;
