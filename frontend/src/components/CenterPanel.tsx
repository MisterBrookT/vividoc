import React, { useState, useEffect, useRef } from 'react';
import { Download } from 'lucide-react';
import toast from 'react-hot-toast';
import DocumentViewer from './DocumentViewer';
import { getDocumentHtml, getDocumentDownloadUrl, getJobStatus, getJobHtml } from '../api/services';
import type { JobStatus } from '../types/models';

interface CenterPanelProps {
  documentId: string | null;
  liveHtml: string | null;
  jobId: string | null;
  onJobCompleted: (documentId: string) => void;
  onLiveHtmlUpdate: (html: string | null) => void;
}

const CenterPanel: React.FC<CenterPanelProps> = ({
  documentId,
  liveHtml,
  jobId,
  onJobCompleted,
  onLiveHtmlUpdate
}) => {
  // Document State
  const [html, setHtml] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Job/Polling State
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const pollingIntervalRef = useRef<number | null>(null);
  const hasCompletedRef = useRef<boolean>(false);

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
        // Toast is handled by the completion logic roughly, avoiding duplicate toasts
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

  // Polling Logic
  useEffect(() => {
    // Reset state when jobId changes
    if (jobId) {
      setJobStatus(null);
      hasCompletedRef.current = false;
    }
  }, [jobId]);

  useEffect(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }

    if (!jobId) {
      setJobStatus(null);
      return;
    }

    const fetchJobStatus = async () => {
      try {
        const status = await getJobStatus(jobId);
        setJobStatus(status);

        // Fetch live HTML
        try {
          const htmlData = await getJobHtml(jobId);
          if (htmlData.html) {
            onLiveHtmlUpdate(htmlData.html);
          }
        } catch (htmlError) {
          // Ignore live html errors
        }

        // Check completion
        if (status.status === 'completed') {
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }

          if (!hasCompletedRef.current && status.result?.document_id) {
            hasCompletedRef.current = true;
            onJobCompleted(status.result.document_id);
          }
        } else if (status.status === 'failed') {
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
          toast.error("Generation Failed");
        }
      } catch (error) {
        console.error('Error fetching job status:', error);
      }
    };

    fetchJobStatus();
    pollingIntervalRef.current = setInterval(fetchJobStatus, 2000);

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [jobId, onJobCompleted, onLiveHtmlUpdate]);


  const handleDownload = () => {
    if (!documentId) return;
    const downloadUrl = getDocumentDownloadUrl(documentId);
    window.open(downloadUrl, '_blank');
  };

  // Helper to determine status text
  const getStatusText = () => {
    if (!jobStatus) return 'Ready';
    if (jobStatus.status === 'failed') return 'Generation Failed';
    if (jobStatus.status === 'completed') return 'Done';

    // Running logic
    const { phase, ku_progress } = jobStatus.progress;
    if (phase === 'planning') return 'Generate Doc Skeleton...';
    if (phase === 'executing') {
      const processingKUs = ku_progress?.filter(k => k.status === 'stage1' || k.status === 'stage2') || [];
      const currentKU = processingKUs[0];
      if (currentKU) {
        // Find index
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

  return (
    <div className="flex-1 flex flex-col relative z-0">
      {/* Header */}
      <div className="h-16 px-6 flex items-center justify-between bg-[var(--bg-panel)] backdrop-blur-sm border-b border-[var(--border-color)] sticky top-0 z-20">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center border border-slate-200 shadow-sm">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" /><polyline points="14 2 14 8 20 8" /></svg>
          </div>
          <div>
            <h2 className="text-sm font-semibold text-[var(--text-primary)]">
              {documentId ? 'Generated Document' : 'Document Preview'}
            </h2>
            {liveHtml && !documentId && (
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <p className="text-[10px] font-medium text-emerald-600 uppercase tracking-wider">Live Preview</p>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Dynamic Status Bar */}
          {isRunning && (
            <div className="flex items-center gap-3 bg-[var(--surface-color)]/50 px-4 py-1.5 rounded-full border border-[var(--border-color)] backdrop-blur-md shadow-sm">
              {/* Colorful Ring Animation */}
              <div className="relative w-5 h-5 flex items-center justify-center">
                <div className="absolute inset-0 rounded-full border-2 border-slate-200/50"></div>
                <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-indigo-500 border-r-purple-500 border-b-pink-500 animate-spin"></div>
                <div className="w-1.5 h-1.5 bg-[var(--accent-primary)] rounded-full animate-pulse"></div>
              </div>
              <span className="text-xs font-semibold text-[var(--text-primary)] tracking-wide">
                {statusText}
              </span>
            </div>
          )}

          {documentId && (
            <button
              onClick={handleDownload}
              disabled={loading || !!error}
              className="inline-flex items-center gap-2 px-4 py-2 btn-primary rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm shadow-lg hover:shadow-indigo-500/25 active:scale-95 fade-in"
            >
              <Download className="w-4 h-4" />
              Download HTML
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
