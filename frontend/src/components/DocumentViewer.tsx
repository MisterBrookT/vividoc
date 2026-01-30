import React, { useState, useEffect } from 'react';
import { FileText, AlertTriangle } from 'lucide-react';

interface DocumentViewerProps {
  html: string | null;
  loading?: boolean;
  error?: string | null;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ 
  html, 
  loading = false,
  error = null 
}) => {
  const [iframeError, setIframeError] = useState<string | null>(null);

  useEffect(() => {
    setIframeError(null);
  }, [html]);

  const handleIframeError = () => {
    setIframeError('Failed to load document');
  };

  if (!html && !loading && !error) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-zinc-950">
        <div className="text-center p-8">
          <div className="w-12 h-12 mx-auto mb-4 bg-zinc-900 rounded-lg flex items-center justify-center border border-zinc-800">
            <FileText className="w-6 h-6 text-zinc-600" />
          </div>
          <p className="text-sm text-zinc-500">
            No document generated yet
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-zinc-950">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-zinc-800 border-t-blue-500 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-zinc-500">Loading document...</p>
        </div>
      </div>
    );
  }

  if (error || iframeError) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-zinc-950">
        <div className="text-center p-8 max-w-md">
          <div className="w-12 h-12 mx-auto mb-4 bg-red-950/50 rounded-lg flex items-center justify-center border border-red-900/50">
            <AlertTriangle className="w-6 h-6 text-red-500" />
          </div>
          <p className="text-sm text-zinc-400">
            {error || iframeError}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-white">
      <iframe
        srcDoc={html || ''}
        className="w-full h-full border-0"
        sandbox="allow-scripts allow-same-origin"
        title="Generated Document"
        onError={handleIframeError}
        style={{
          minHeight: '100%',
          minWidth: '100%',
        }}
      />
    </div>
  );
};

export default DocumentViewer;
