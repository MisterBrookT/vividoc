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
    },
    completed: {
      label: 'Complete',
      description: 'Ready for download.',
      icon: '✓'
    }
  };



  const currentPhase = (status === 'completed' || progress.overall_percent === 100)
    ? phaseConfig.completed
    : phaseConfig[progress.phase] || phaseConfig.planning;

  const statusConfig = {
    running: {
      label: 'Running',
      color: 'text-blue-600',
      dotColor: 'bg-blue-600',
    },
    completed: {
      label: 'Completed',
      color: 'text-green-600',
      dotColor: 'bg-green-600',
    },
    failed: {
      label: 'Failed',
      color: 'text-red-600',
      dotColor: 'bg-red-600',
    }
  };

  const statusBadge = statusConfig[status];

  return (
    <div className="space-y-6" data-testid="progress-monitor">
      {/* Header & Status */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-[var(--text-primary)]">Generation Status</h2>
          <p className="text-xs text-[var(--text-secondary)]">Tracking document creation</p>
        </div>
        <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-full border border-slate-100 shadow-sm">
          <span className={`w-2 h-2 rounded-full ${statusBadge.dotColor} animate-pulse`} />
          <span className={`text-xs font-semibold ${statusBadge.color}`}>
            {statusBadge.label}
          </span>
        </div>
      </div>

      {/* Overall Progress Bar */}
      <div>
        <ProgressBar percent={progress.overall_percent} showLabel={true} height="sm" />
      </div>

      {/* Current Phase Card */}
      <div className="bg-white rounded-xl p-4 border border-slate-100 shadow-sm relative overflow-hidden">
        <div className={`absolute top-0 left-0 w-1 h-full ${status === 'failed' ? 'bg-red-500' : 'bg-[var(--accent-primary)]'}`} />
        <div className="flex items-start gap-4">
          <div className="p-2 bg-slate-50 rounded-lg">
            <span className="text-xl" role="img" aria-label={currentPhase.label}>
              {currentPhase.icon}
            </span>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-[var(--text-primary)]">
              {currentPhase.label}
            </h3>
            <p className="text-xs text-[var(--text-secondary)] mt-0.5">
              {currentPhase.description}
            </p>
          </div>
        </div>
      </div>

      {/* Knowledge Units Progress */}
      {progress.ku_progress && progress.ku_progress.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-bold text-[var(--text-secondary)] uppercase tracking-wider">
              Knowledge Units
            </h3>
            <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
              {progress.ku_progress.length}
            </span>
          </div>
          <div className="space-y-2">
            {progress.ku_progress.map((ku) => (
              <KUProgressCard key={ku.ku_id} ku={ku} />
            ))}
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div
          className="bg-red-50 border border-red-100 rounded-xl p-4"
          data-testid="error-message"
          role="alert"
        >
          <div className="flex items-start gap-3">
            <div className="p-1.5 bg-red-100 rounded-md">
              <span className="text-red-600 text-sm block">✕</span>
            </div>
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-red-900">generation Failed</h4>
              <p className="text-xs text-red-700 mt-1 leading-relaxed">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Completion Message Removed */}
    </div>
  );
};

export default ProgressMonitor;
