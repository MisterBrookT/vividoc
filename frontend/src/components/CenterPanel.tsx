
import React, { useState, useEffect } from 'react';
import { Download, ChevronRight, FileText, Layout, FileCode } from 'lucide-react';
import toast from 'react-hot-toast';
import DocumentViewer from './DocumentViewer';
import { getDocumentHtml, getDocumentDownloadUrl } from '../api/services';
import type { JobStatus, DocumentSpec } from '../types/models';

interface CenterPanelProps {
  documentId: string | null;
  liveHtml: string | null;
  jobStatus: JobStatus | null;
  spec: DocumentSpec | null;
  onViewSpec: () => void;
}

const CenterPanel: React.FC<CenterPanelProps> = ({
  documentId,
  liveHtml,
  jobStatus,
  spec,
  onViewSpec,
}) => {
  // Document State
  const [html, setHtml] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sync liveHtml
  useEffect(() => {
    if (liveHtml) {
      setHtml(liveHtml);
    }
  }, [liveHtml]);

  // Fetch final document HTML
  useEffect(() => {
    if (!documentId) {
      if (!liveHtml) {
        setHtml(null);
      }
      setError(null);
      return;
    }

    const fetchHtml = async () => {
      setLoading(true);
      setError(null);

      try {
        const htmlContent = await getDocumentHtml(documentId);
        setHtml(htmlContent);
      } catch (err) {
        console.error('Failed to fetch document HTML:', err);
        setError('Failed to load document');
        toast.error('Failed to load document');
      } finally {
        setLoading(false);
      }
    };

    fetchHtml();
  }, [documentId, liveHtml]);


  const handleDownload = () => {
    if (!documentId) return;
    const downloadUrl = getDocumentDownloadUrl(documentId);
    window.open(downloadUrl, '_blank');
  };

  // Helper to determine status text for tooltip/hover
  const getStatusText = () => {
    if (!jobStatus) return 'Ready';
    if (jobStatus.status === 'failed') return 'Generation Failed';
    if (jobStatus.status === 'completed') return 'Done';

    // Running logic
    const { phase, ku_progress } = jobStatus.progress;
    if (phase === 'planning') return 'Generate Doc Skeleton...';
    if (phase === 'executing') {
      // ... existing logic ...
      const processingKUs = ku_progress?.filter(k => k.status === 'stage1' || k.status === 'stage2') || [];
      const currentKU = processingKUs[0];
      if (currentKU) {
        const index = ku_progress.findIndex(k => k.ku_id === currentKU.ku_id);
        return `Generating KU ${index + 1}...`;
      }
      return 'Generating content...';
    }
    if (phase === 'evaluating') return 'Refining...';
    return 'Initializing...';
  };

  const statusText = getStatusText();
  const isRunning = jobStatus?.status === 'running';

  // Navigation Steps Logic
  const steps = [
    {
      id: 'topic',
      label: 'Topic',
      icon: Layout,
      active: true, // Always active
      current: !spec && !documentId, // Is specifically current state?
      onClick: () => { }
    },
    {
      id: 'spec',
      label: 'Spec',
      icon: FileText,
      active: !!spec, // Active if spec exists
      current: !!spec && !documentId && !isRunning,
      onClick: spec ? onViewSpec : undefined
    },
    {
      id: 'doc',
      label: 'Doc',
      icon: FileCode,
      active: !!documentId || !!liveHtml || isRunning,
      current: !!documentId || !!liveHtml || isRunning,
      onClick: () => { }
    }
  ];

  return (
    <div className="flex-1 h-full flex flex-col relative z-0">
      {/* Header */}
      <div className="h-16 flex-shrink-0 px-6 flex items-center justify-between bg-[var(--bg-panel)] backdrop-blur-sm border-b border-[var(--border-color)] z-20">

        {/* Navigation Steppers */}
        <div className="flex items-center gap-1">
          {steps.map((step, index) => (
            <React.Fragment key={step.id}>
              <button
                onClick={step.onClick}
                disabled={!step.active}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all ${step.active
                    ? 'text-[var(--text-primary)] hover:bg-white/60 cursor-pointer'
                    : 'text-slate-300 cursor-not-allowed'
                  } ${step.current ? 'bg-white shadow-sm ring-1 ring-slate-200/50' : ''}`}
              >
                <step.icon className={`w-4 h-4 ${step.active ? 'text-[var(--accent-primary)]' : 'text-slate-300'}`} />
                <span className={`text-sm font-medium ${step.active ? 'text-slate-700' : 'text-slate-400'}`}>{step.label}</span>
              </button>

              {index < steps.length - 1 && (
                <ChevronRight className={`w-4 h-4 ${steps[index + 1].active ? 'text-slate-400' : 'text-slate-200'}`} />
              )}
            </React.Fragment>
          ))}
        </div>

        <div className="flex items-center gap-4">
          {/* Status Indicator (Compact) */}
          {isRunning && (
            <div className="flex items-center gap-2 px-3 py-1 bg-indigo-50/50 rounded-full border border-indigo-100">
              <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse" />
              <span className="text-xs font-medium text-indigo-600 truncate max-w-[150px]">{statusText}</span>
            </div>
          )}

          {documentId && (
            <button
              onClick={handleDownload}
              disabled={loading || !!error}
              className="inline-flex items-center gap-2 px-4 py-2 btn-primary rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm shadow-lg hover:shadow-indigo-500/25 active:scale-95 fade-in"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </button>
          )}
        </div>
      </div>

      {/* Document viewer */}
      <div className="flex-1 overflow-hidden">
        <DocumentViewer
          html={html}
          loading={loading && !html} // Only show big loader if no HTML yet
          error={error}
        />
      </div>
    </div>
  );
};

export default CenterPanel;
