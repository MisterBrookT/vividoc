import React, { useState, useEffect } from 'react';
import DocumentViewer from './DocumentViewer';
import { getDocumentHtml, getDocumentDownloadUrl } from '../api/services';

/**
 * CenterPanel Component
 * 
 * Displays the generated HTML document with download functionality.
 * 
 * Features:
 * - Integrates DocumentViewer component for HTML rendering
 * - Fetches HTML content when documentId changes
 * - Provides download button to save document locally
 * - Handles loading and error states
 * 
 * Requirements: 5.1, 6.2
 */

interface CenterPanelProps {
  /** Document ID to display, null if no document is generated yet */
  documentId: string | null;
  /** Live HTML content being generated (real-time preview) */
  liveHtml: string | null;
}

const CenterPanel: React.FC<CenterPanelProps> = ({ documentId, liveHtml }) => {
  const [html, setHtml] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Update HTML when liveHtml changes (real-time preview)
  useEffect(() => {
    if (liveHtml) {
      setHtml(liveHtml);
    }
  }, [liveHtml]);

  // Fetch HTML content when documentId changes (final document)
  useEffect(() => {
    if (!documentId) {
      // Don't clear HTML if we have liveHtml
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
        setError('Failed to load document. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchHtml();
  }, [documentId, liveHtml]);

  // Handle download button click - open download endpoint in new tab
  const handleDownload = () => {
    if (!documentId) return;
    
    const downloadUrl = getDocumentDownloadUrl(documentId);
    window.open(downloadUrl, '_blank');
  };

  return (
    <div className="flex-1 flex flex-col bg-gray-50">
      {/* Header with download button */}
      {documentId && (
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">
            Generated Document
          </h2>
          <button
            onClick={handleDownload}
            disabled={loading || !!error}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Download HTML document"
          >
            <svg
              className="mr-2 h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            Download HTML
          </button>
        </div>
      )}

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
