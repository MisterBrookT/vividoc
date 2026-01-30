import React, { useEffect, useRef, useState } from 'react';
import ProgressMonitor from './ProgressMonitor';
import { getJobStatus, getJobHtml } from '../api/services';
import type { JobStatus } from '../types/models';

interface RightPanelProps {
  jobId: string | null;
  onJobCompleted: (documentId: string) => void;
  onLiveHtmlUpdate: (html: string | null) => void;
}

/**
 * RightPanel component for displaying real-time progress monitoring.
 * 
 * Features:
 * - Integrates ProgressMonitor component for visual progress display
 * - Implements polling mechanism (every 2 seconds) to fetch job status
 * - Automatically stops polling when job completes or fails
 * - Handles polling errors gracefully with retry logic
 * - Invokes onJobCompleted callback when document generation completes
 * - Cleans up polling interval on unmount or when jobId changes
 * 
 * Requirements: 4.1, 4.2, 4.4, 4.5
 */
const RightPanel: React.FC<RightPanelProps> = ({ jobId, onJobCompleted, onLiveHtmlUpdate }) => {
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [pollingError, setPollingError] = useState<string | null>(null);
  const pollingIntervalRef = useRef<number | null>(null);
  const hasCompletedRef = useRef<boolean>(false);

  useEffect(() => {
    // Reset state when jobId changes
    if (jobId) {
      setJobStatus(null);
      setPollingError(null);
      hasCompletedRef.current = false;
    }
  }, [jobId]);

  useEffect(() => {
    // Clear any existing polling interval
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }

    // If no jobId, nothing to poll
    if (!jobId) {
      setJobStatus(null);
      return;
    }

    // Function to fetch job status
    const fetchJobStatus = async () => {
      try {
        const status = await getJobStatus(jobId);
        setJobStatus(status);
        setPollingError(null); // Clear any previous errors

        // Fetch live HTML during generation
        try {
          const htmlData = await getJobHtml(jobId);
          if (htmlData.html) {
            onLiveHtmlUpdate(htmlData.html);
          }
        } catch (htmlError) {
          console.error('Error fetching live HTML:', htmlError);
          // Don't fail the whole polling if HTML fetch fails
        }

        // Check if job is complete or failed
        if (status.status === 'completed') {
          // Stop polling
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }

          // Invoke callback only once
          if (!hasCompletedRef.current && status.result?.document_id) {
            hasCompletedRef.current = true;
            onJobCompleted(status.result.document_id);
          }
        } else if (status.status === 'failed') {
          // Stop polling on failure
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
        }
      } catch (error) {
        // Handle polling errors gracefully
        console.error('Error fetching job status:', error);
        
        // Set error message but continue polling (transient errors)
        const errorMessage = error instanceof Error 
          ? error.message 
          : 'Failed to fetch job status';
        setPollingError(errorMessage);
        
        // Don't stop polling on error - it might be transient
        // The interval will continue and retry
      }
    };

    // Fetch immediately on mount/jobId change
    fetchJobStatus();

    // Set up polling interval (every 2 seconds)
    pollingIntervalRef.current = setInterval(fetchJobStatus, 2000);

    // Cleanup function
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [jobId, onJobCompleted, onLiveHtmlUpdate]);

  // If no jobId, show placeholder
  if (!jobId) {
    return (
      <div className="w-1/4 border-l border-gray-200 bg-white p-6" data-testid="right-panel">
        <div className="text-center text-gray-500 py-8">
          <p className="text-lg font-medium">No Active Job</p>
          <p className="text-sm mt-2">
            Generate a document to see progress here
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-1/4 border-l border-gray-200 bg-white p-6 overflow-y-auto" data-testid="right-panel">
      {/* Polling Error Banner */}
      {pollingError && (
        <div 
          className="mb-4 bg-yellow-50 border border-yellow-300 rounded-lg p-3"
          data-testid="polling-error"
          role="alert"
        >
          <div className="flex items-start gap-2">
            <span className="text-yellow-600 text-sm" role="img" aria-label="Warning">
              ⚠️
            </span>
            <div className="flex-1">
              <p className="text-xs text-yellow-800">
                <strong>Connection Issue:</strong> {pollingError}
              </p>
              <p className="text-xs text-yellow-700 mt-1">
                Retrying automatically...
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Progress Monitor */}
      <ProgressMonitor jobStatus={jobStatus} />
    </div>
  );
};

export default RightPanel;
