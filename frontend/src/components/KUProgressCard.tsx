import React from 'react';
import type { KUProgress } from '../types/models';

interface KUProgressCardProps {
  ku: KUProgress;
}

/**
 * KUProgressCard component for displaying knowledge unit progress status.
 * 
 * Features:
 * - Displays KU title and status badge
 * - Color-coded status badges:
 *   - pending: gray
 *   - stage1: yellow (text generation in progress)
 *   - stage2: blue (code generation in progress)
 *   - completed: green
 * - Compact card design for progress monitoring
 * 
 * Requirements: 4.3, 4.4
 */
const KUProgressCard: React.FC<KUProgressCardProps> = ({ ku }) => {
  // Status badge configuration
  const statusConfig = {
    pending: {
      label: 'Pending',
      bgColor: 'bg-gray-200',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-300'
    },
    stage1: {
      label: 'Stage 1',
      bgColor: 'bg-yellow-100',
      textColor: 'text-yellow-800',
      borderColor: 'border-yellow-300'
    },
    stage2: {
      label: 'Stage 2',
      bgColor: 'bg-blue-100',
      textColor: 'text-blue-800',
      borderColor: 'border-blue-300'
    },
    completed: {
      label: 'Completed',
      bgColor: 'bg-green-100',
      textColor: 'text-green-800',
      borderColor: 'border-green-300'
    }
  };

  const config = statusConfig[ku.status];

  return (
    <div 
      className={`ku-progress-card border rounded-lg p-3 mb-2 transition-all duration-200 ${config.borderColor}`}
      data-testid={`ku-progress-${ku.ku_id}`}
    >
      <div className="flex items-start justify-between gap-2">
        {/* KU Title */}
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium text-gray-900 truncate" title={ku.title}>
            {ku.title}
          </h4>
        </div>

        {/* Status Badge */}
        <div className="flex-shrink-0">
          <span 
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bgColor} ${config.textColor}`}
            data-testid={`status-badge-${ku.status}`}
          >
            {config.label}
          </span>
        </div>
      </div>

      {/* Optional: Progress indicator for active stages */}
      {(ku.status === 'stage1' || ku.status === 'stage2') && (
        <div className="mt-2">
          <div className="flex items-center gap-2 text-xs text-gray-600">
            <div className="animate-pulse flex space-x-1">
              <div className="w-1.5 h-1.5 bg-gray-400 rounded-full"></div>
              <div className="w-1.5 h-1.5 bg-gray-400 rounded-full"></div>
              <div className="w-1.5 h-1.5 bg-gray-400 rounded-full"></div>
            </div>
            <span>
              {ku.status === 'stage1' ? 'Generating text...' : 'Generating code...'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default KUProgressCard;
