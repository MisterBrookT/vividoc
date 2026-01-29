import React, { useState } from 'react';
import TopicInput from './TopicInput';
import SpecEditor from './SpecEditor';
import type { DocumentSpec } from '../types/models';
import { generateSpec, updateSpec, generateDocument } from '../api/services';

interface LeftSidebarProps {
  spec: DocumentSpec | null;
  onSpecGenerated: (specId: string, spec: DocumentSpec) => void;
  onSpecUpdated: (spec: DocumentSpec) => void;
  onGenerateDocument: (jobId: string) => void;
}

/**
 * LeftSidebar component that integrates TopicInput and SpecEditor.
 * 
 * Features:
 * - Topic input and spec generation
 * - Spec editing (edit, delete, reorder KUs)
 * - Document generation trigger
 * - Error handling and display
 * 
 * Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.2, 2.3, 2.4, 2.6, 3.1
 */
const LeftSidebar: React.FC<LeftSidebarProps> = ({
  spec,
  onSpecGenerated,
  onSpecUpdated,
  onGenerateDocument,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatingDocument, setGeneratingDocument] = useState(false);

  /**
   * Handle spec generation from topic input
   * Requirements: 1.1, 1.2, 1.3, 1.4
   */
  const handleGenerateSpec = async (topic: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await generateSpec(topic);
      onSpecGenerated(response.spec_id, response.spec);
    } catch (err: any) {
      // Requirement 1.5: Display error message on failure
      const errorMessage =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        'Failed to generate specification. Please try again.';
      setError(errorMessage);
      console.error('Spec generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle spec updates (edit, delete, reorder KUs)
   * Requirements: 2.2, 2.3, 2.4, 2.6
   */
  const handleSpecUpdate = async (updatedSpec: DocumentSpec) => {
    if (!spec) return;

    setError(null);

    try {
      const response = await updateSpec(spec.id, updatedSpec);
      onSpecUpdated(response.spec);
    } catch (err: any) {
      // Display error message on update failure
      const errorMessage =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        'Failed to update specification. Please try again.';
      setError(errorMessage);
      console.error('Spec update error:', err);
    }
  };

  /**
   * Handle document generation trigger
   * Requirement: 3.1
   */
  const handleGenerateDocument = async () => {
    if (!spec) return;

    setGeneratingDocument(true);
    setError(null);

    try {
      const response = await generateDocument(spec.id);
      onGenerateDocument(response.job_id);
    } catch (err: any) {
      // Display error message on generation failure
      const errorMessage =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        'Failed to start document generation. Please try again.';
      setError(errorMessage);
      console.error('Document generation error:', err);
    } finally {
      setGeneratingDocument(false);
    }
  };

  /**
   * Dismiss error message
   */
  const handleDismissError = () => {
    setError(null);
  };

  return (
    <div className="w-1/4 min-w-[300px] max-w-[400px] border-r border-gray-200 bg-white overflow-y-auto">
      <div className="p-6">
        {/* Error Display - Requirement 1.5 */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-red-800 mb-1">Error</h3>
                <p className="text-sm text-red-700">{error}</p>
              </div>
              <button
                onClick={handleDismissError}
                className="ml-2 text-red-400 hover:text-red-600 transition-colors"
                aria-label="Dismiss error"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Topic Input - Requirements 1.1, 1.2, 1.3, 1.4 */}
        <TopicInput onSubmit={handleGenerateSpec} loading={loading} />

        {/* Spec Editor - Requirements 2.2, 2.3, 2.4, 2.6, 3.1 */}
        {spec && (
          <SpecEditor
            spec={spec}
            onUpdate={handleSpecUpdate}
            onGenerate={handleGenerateDocument}
          />
        )}

        {/* Loading indicator for document generation */}
        {generatingDocument && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center">
              <svg
                className="animate-spin h-5 w-5 text-blue-600 mr-3"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <span className="text-sm text-blue-700 font-medium">
                Starting document generation...
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LeftSidebar;
