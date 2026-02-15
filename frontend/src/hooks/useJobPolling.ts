
import { useState, useEffect, useRef } from 'react';
import { getJobStatus, getJobHtml } from '../api/services';
import type { JobStatus } from '../types/models';
import toast from 'react-hot-toast';

interface UseJobPollingResult {
    jobStatus: JobStatus | null;
    liveHtml: string | null;
    error: string | null;
}

export const useJobPolling = (
    jobId: string | null,
    onJobCompleted?: (documentId: string) => void,
    onLiveHtmlUpdate?: (html: string | null) => void
): UseJobPollingResult => {
    const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
    const [liveHtml, setLiveHtml] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const pollingIntervalRef = useRef<number | null>(null);
    const hasCompletedRef = useRef<boolean>(false);

    // Reset state when jobId changes
    useEffect(() => {
        if (jobId) {
            setJobStatus(null);
            setLiveHtml(null);
            setError(null);
            hasCompletedRef.current = false;
        }
    }, [jobId]);

    useEffect(() => {
        // Clear existing interval
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

                // Fetch live HTML if running
                if (status.status === 'running') {
                    try {
                        const htmlData = await getJobHtml(jobId);
                        if (htmlData.html) {
                            setLiveHtml(htmlData.html);
                            if (onLiveHtmlUpdate) onLiveHtmlUpdate(htmlData.html);
                        }
                    } catch (htmlError) {
                        // Ignore live html errors
                    }
                }

                // Check completion
                if (status.status === 'completed') {
                    if (pollingIntervalRef.current) {
                        clearInterval(pollingIntervalRef.current);
                        pollingIntervalRef.current = null;
                    }

                    if (!hasCompletedRef.current && status.result?.document_id) {
                        hasCompletedRef.current = true;
                        if (onJobCompleted) onJobCompleted(status.result.document_id);
                    }
                } else if (status.status === 'failed') {
                    if (pollingIntervalRef.current) {
                        clearInterval(pollingIntervalRef.current);
                        pollingIntervalRef.current = null;
                    }
                    setError(status.error || 'Generation Failed');
                    toast.error("Generation Failed");
                }
            } catch (err) {
                console.error('Error fetching job status:', err);
                // Don't set error state immediately to avoid flashing error on transient network issues, 
                // but maybe log it. 
            }
        };

        fetchJobStatus();
        pollingIntervalRef.current = window.setInterval(fetchJobStatus, 2000);

        return () => {
            if (pollingIntervalRef.current) {
                clearInterval(pollingIntervalRef.current);
                pollingIntervalRef.current = null;
            }
        };
    }, [jobId, onJobCompleted, onLiveHtmlUpdate]);

    return { jobStatus, liveHtml, error };
};
