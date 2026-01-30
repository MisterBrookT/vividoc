import React, { useEffect, useRef, useState } from 'react';
import { Activity } from 'lucide-react';
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
      <div className="w-80 glass-panel border-l border-[var(--border-color)] p-6 relative z-10 flex flex-col items-center justify-center h-full" data-testid="right-panel">
        <div className="text-center">
          <div className="w-16 h-16 mb-6 bg-slate-100 rounded-full flex items-center justify-center mx-auto ring-4 ring-slate-50">
            <Activity className="w-6 h-6 text-indigo-500" />
          </div>
          <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-1">
            Ready to Generate
          </h3>
          <p className="text-xs text-[var(--text-secondary)] max-w-[200px] mx-auto leading-relaxed">
            Select a topic and generate a spec to start creating your document.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-80 glass-panel border-l border-[var(--border-color)] flex flex-col h-full relative z-10" data-testid="right-panel">

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Polling Error Banner - Sophisticated Style */}
        {pollingError && (
          <div
            className="bg-amber-50 border border-amber-200 rounded-lg p-3 flex gap-3 shadow-sm"
            data-testid="polling-error"
            role="alert"
          >
            <span className="text-amber-500 mt-0.5">⚠️</span>
            <div className="flex-1">
              <p className="text-xs font-medium text-amber-800">
                Connection Paused
              </p>
              <p className="text-[10px] text-amber-600 mt-0.5 leading-tight">
                {pollingError}. Retrying...
              </p>
            </div>
          </div>
        )}

        <ProgressMonitor jobStatus={jobStatus} />
      </div>
    </div>
  );
};

export default RightPanel;
