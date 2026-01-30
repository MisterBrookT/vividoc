import React, { useState, useEffect } from 'react';
import { Download } from 'lucide-react';
import toast from 'react-hot-toast';
import DocumentViewer from './DocumentViewer';
import { getDocumentHtml, getDocumentDownloadUrl } from '../api/services';

interface CenterPanelProps {
  documentId: string | null;
  liveHtml: string | null;
}

const CenterPanel: React.FC<CenterPanelProps> = ({ documentId, liveHtml }) => {
  const [html, setHtml] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (liveHtml) {
      setHtml(liveHtml);
    }
  }, [liveHtml]);

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
        toast.success('Document loaded');
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
    toast.success('Download started');
  };

  return (
    <div className="flex-1 flex flex-col relative z-0">
      {/* Header */}
      <div className="h-16 px-6 flex items-center justify-between bg-zinc-900/50 backdrop-blur-sm border-b border-white/5 sticky top-0 z-20">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-zinc-800/50 flex items-center justify-center border border-white/5">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 text-zinc-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" /><polyline points="14 2 14 8 20 8" /></svg>
          </div>
          <div>
            <h2 className="text-sm font-semibold text-zinc-100">
              {documentId ? 'Generated Document' : 'Document Preview'}
            </h2>
            {liveHtml && !documentId && (
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <p className="text-[10px] font-medium text-emerald-500 uppercase tracking-wider">Live Preview</p>
              </div>
            )}
          </div>
        </div>

        {documentId && (
          <button
            onClick={handleDownload}
            disabled={loading || !!error}
            className="inline-flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-100 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm border border-white/5 shadow-lg hover:shadow-zinc-500/10 active:scale-95"
          >
            <Download className="w-4 h-4" />
            Download HTML
          </button>
        )}
      </div>

      {/* Document viewer */}
      <div className="flex-1 overflow-hidden">
        <DocumentViewer
          html={html}
          loading={loading}
          error={error}
        />
      </div>
    </div>
  );
};

export default CenterPanel;
