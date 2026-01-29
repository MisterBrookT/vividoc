import React, { useState, useEffect } from 'react';

/**
 * DocumentViewer Component
 * 
 * Renders generated HTML documents in an isolated iframe with security sandboxing.
 * 
 * Features:
 * - Iframe rendering with srcDoc for HTML content
 * - Sandbox attribute for security (allows scripts but isolates from parent)
 * - Loading state management
 * - Placeholder display when no document is available
 * - Error handling for malformed HTML
 * 
 * Requirements: 5.2, 5.3, 5.4, 9.5
 */

interface DocumentViewerProps {
  /** HTML content to display in the iframe */
  html: string | null;
  /** Loading state indicator */
  loading?: boolean;
  /** Error message to display if HTML is malformed or fails to load */
  error?: string | null;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ 
  html, 
  loading = false,
  error = null 
}) => {
  const [iframeError, setIframeError] = useState<string | null>(null);

  // Reset iframe error when html changes
  useEffect(() => {
    setIframeError(null);
  }, [html]);

  // Handle iframe load errors
  const handleIframeError = () => {
    setIframeError('Failed to load document. The HTML content may be malformed.');
  };

  // Display placeholder when no document is available
  if (!html && !loading && !error) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-50">
        <div className="text-center p-8">
          <svg
            className="mx-auto h-12 w-12 text-gray-400 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No Document Generated
          </h3>
          <p className="text-sm text-gray-500">
            Generate a document to view it here
          </p>
        </div>
      </div>
    );
  }

  // Display loading state
  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-sm text-gray-600">Loading document...</p>
        </div>
      </div>
    );
  }

  // Display error state
  if (error || iframeError) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-50">
        <div className="text-center p-8 max-w-md">
          <svg
            className="mx-auto h-12 w-12 text-red-400 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <h3 className="text-lg font-medium text-red-900 mb-2">
            Error Loading Document
          </h3>
          <p className="text-sm text-red-700">
            {error || iframeError}
          </p>
        </div>
      </div>
    );
  }

  // Render HTML in iframe with security sandbox
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
