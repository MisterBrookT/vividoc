import { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import type { DocumentSpec } from './types/models';
import LeftSidebar from './components/LeftSidebar';
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
  const [configModalOpen, setConfigModalOpen] = useState(false);
  const [isSpecGenerating, setIsSpecGenerating] = useState(false);
  const [theme, setTheme] = useState<'default' | 'warm'>('default');
  // Track whether spec was freshly generated (not loaded from history)
  const [specJustGenerated, setSpecJustGenerated] = useState(false);

  const { jobStatus, liveHtml: polledHtml } = useJobPolling(
    jobId,
    (docId) => setDocumentId(docId),
    (html) => setLiveHtml(html)
  );

  const handleSpecGenerationStart = () => {
    setIsSpecGenerating(true);
    setSpecJustGenerated(false);
  };

  const handleSpecGenerated = (id: string, newSpec: DocumentSpec) => {
    setSpec({ ...newSpec, id });
    setDocumentId(null);
    setJobId(null);
    setLiveHtml(null);
    setIsSpecGenerating(false);
    setSpecJustGenerated(true);
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
      setSpecJustGenerated(false);

      const htmlContent = await getSpecHtml(specId);
      if (htmlContent) {
        setLiveHtml(htmlContent);
      }
    } catch (error) {
      console.error("Failed to load history item", error);
    }
  };

  const handleNewDoc = () => {
    setSpec(null);
    setDocumentId(null);
    setJobId(null);
    setLiveHtml(null);
    setSpecJustGenerated(false);
  };

  const handleSendMessage = (message: string) => {
    console.log("User message:", message);
  };

  // Compute active stage for chat context
  const getActiveStage = (): 'topic' | 'spec' | 'style' | 'doc' => {
    if (documentId || liveHtml || polledHtml || jobStatus?.status === 'running') return 'doc';
    if (spec) return 'spec';
    return 'topic';
  };

  const toggleTheme = () => {
    const newTheme = theme === 'default' ? 'warm' : 'default';
    setTheme(newTheme);
    if (newTheme === 'warm') {
      document.documentElement.setAttribute('data-theme', 'warm');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    // Broadcast theme change to any embedded iframes
    setTimeout(() => {
      document.querySelectorAll('iframe').forEach(iframe => {
        iframe.contentWindow?.postMessage({ type: 'THEME_CHANGE', theme: newTheme }, '*');
      });
    }, 50);
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
            iconTheme: { primary: '#22c55e', secondary: '#fff' },
          },
          error: {
            iconTheme: { primary: '#ef4444', secondary: '#fff' },
          },
        }}
      />

      <div className="fixed inset-0 bg-[var(--bg-app)] selection:bg-primary-500/30 selection:text-primary-200 overflow-hidden flex">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-900/10 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary-900/10 rounded-full blur-[100px] pointer-events-none" />

        <LeftSidebar
          onSelectHistory={handleSelectHistory}
          onNewDoc={handleNewDoc}
          configModalOpen={configModalOpen}
          onConfigModalChange={setConfigModalOpen}
          currentSpecId={spec?.id || null}
          theme={theme}
          onToggleTheme={toggleTheme}
        />

        <CenterPanel
          spec={spec}
          documentId={documentId}
          liveHtml={polledHtml || liveHtml}
          jobStatus={jobStatus}
          isSpecGenerating={isSpecGenerating}
          onSpecGenerated={handleSpecGenerated}
          onSpecGenerationStart={handleSpecGenerationStart}
          onSpecUpdated={handleSpecUpdated}
          onGenerateDocument={handleGenerateDocument}
          theme={theme}
        />

        <RightChatPanel
          jobStatus={jobStatus}
          onSendMessage={handleSendMessage}
          isGeneratingSpec={isSpecGenerating}
          spec={spec}
          specJustGenerated={specJustGenerated}
          onSpecJustGeneratedConsumed={() => setSpecJustGenerated(false)}
          onHtmlUpdated={(html) => setLiveHtml(html)}
          onSpecUpdated={handleSpecUpdated}
          activeStage={getActiveStage()}
          theme={theme}
        />
      </div>
    </>
  );
}

export default App;
