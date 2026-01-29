import React from 'react';
import ProgressBar from './ProgressBar';
import KUProgressCard from './KUProgressCard';
import type { JobStatus } from '../types/models';

interface ProgressMonitorProps {
  jobStatus: JobStatus | null;
}

/**
 * ProgressMonitor component for displaying real-time document generation progress.
 * 
 * Features:
 * - Overall progress bar showing percentage completion
 * - Current phase display (planning, executing, evaluating)
 * - Job status display (running, completed, failed)
 * - List of KU progress cards showing individual knowledge unit status
 * - Error message display if job fails
 * - Handles null/undefined jobStatus gracefully
 * 
 * Requirements: 4.4, 4.5
 */
const ProgressMonitor: React.FC<ProgressMonitorProps> = ({ jobStatus }) => {
  // If no job status, show placeholder
  if (!jobStatus) {
    return (
      <div className="progress-monitor">
        <div className="text-center text-gray-500 py-8">
          <p>No active job</p>
          <p className="text-sm mt-2">Start document generation to see progress</p>
        </div>
      </div>
    );
  }

  const { status, progress, error } = jobStatus;

  // Phase display configuration
  const phaseConfig = {
    planning: {
      label: 'Planning',
      description: 'Generating document structure...',
      icon: '📋'
    },
    executing: {
      label: 'Executing',
      description: 'Generating content...',
      icon: '⚙️'
    },
    evaluating: {
      label: 'Evaluating',
      description: 'Assessing content quality...',
      icon: '✓'
    }
  };

  const currentPhase = phaseConfig[progress.phase];

  // Status badge configuration
  const statusConfig = {
    running: {
      label: 'Running',
      bgColor: 'bg-blue-100',
      textColor: 'text-blue-800',
      borderColor: 'border-blue-300'
    },
    completed: {
      label: 'Completed',
      bgColor: 'bg-green-100',
      textColor: 'text-green-800',
      borderColor: 'border-green-300'
    },
    failed: {
      label: 'Failed',
      bgColor: 'bg-red-100',
      textColor: 'text-red-800',
      borderColor: 'border-red-300'
    }
  };

  const statusBadge = statusConfig[status];

  return (
    <div className="progress-monitor space-y-4" data-testid="progress-monitor">
      {/* Status Badge */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Progress</h2>
        <span 
          className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusBadge.bgColor} ${statusBadge.textColor}`}
          data-testid="status-badge"
        >
          {statusBadge.label}
        </span>
      </div>

      {/* Overall Progress Bar */}
      <div className="progress-section">
        <ProgressBar percent={progress.overall_percent} showLabel={true} height="md" />
      </div>

      {/* Current Phase */}
      <div className="phase-section bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div className="flex items-start gap-3">
          <span className="text-2xl" role="img" aria-label={currentPhase.label}>
            {currentPhase.icon}
          </span>
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-gray-900">
              Current Phase: {currentPhase.label}
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {currentPhase.description}
            </p>
          </div>
        </div>
      </div>

      {/* Knowledge Units Progress */}
      {progress.ku_progress && progress.ku_progress.length > 0 && (
        <div className="ku-progress-section">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">
            Knowledge Units ({progress.ku_progress.length})
          </h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {progress.ku_progress.map((ku) => (
              <KUProgressCard key={ku.ku_id} ku={ku} />
            ))}
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div 
          className="error-message bg-red-50 border border-red-300 rounded-lg p-4"
          data-testid="error-message"
          role="alert"
        >
          <div className="flex items-start gap-3">
            <span className="text-red-600 text-xl" role="img" aria-label="Error">
              ⚠️
            </span>
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-red-900 mb-1">
                Job Failed
              </h4>
              <p className="text-sm text-red-700">
                {error}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Completion Message */}
      {status === 'completed' && !error && (
        <div 
          className="completion-message bg-green-50 border border-green-300 rounded-lg p-4"
          data-testid="completion-message"
        >
          <div className="flex items-start gap-3">
            <span className="text-green-600 text-xl" role="img" aria-label="Success">
              ✅
            </span>
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-green-900 mb-1">
                Document Generated Successfully
              </h4>
              <p className="text-sm text-green-700">
                Your document is ready to view and download.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProgressMonitor;
