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
  // Status badge configuration - minimal dots
  const statusConfig = {
    pending: { label: 'Pending', color: 'bg-slate-300' },
    stage1: { label: 'Drafting', color: 'bg-amber-400' },
    stage2: { label: 'Refining', color: 'bg-indigo-500' },
    completed: { label: 'Done', color: 'bg-emerald-500' }
  };

  const config = statusConfig[ku.status];

  return (
    <div
      className="bg-white rounded-lg p-3 shadow-sm border border-slate-100 hover:shadow-md transition-shadow duration-200 group"
      data-testid={`ku-progress-${ku.ku_id}`}
    >
      <div className="flex items-center gap-3">
        {/* Status Dot */}
        <div className={`w-2 h-2 rounded-full flex-shrink-0 ${config.color} ${ku.status.includes('stage') ? 'animate-pulse' : ''}`} />

        {/* Title */}
        <div className="flex-1 min-w-0">
          <h4 className="text-xs font-medium text-[var(--text-primary)] truncate" title={ku.title}>
            {ku.title}
          </h4>
        </div>

        {/* Status Label (only if active/completed) */}
        {ku.status !== 'pending' && (
          <span className="text-[10px] text-[var(--text-secondary)] font-medium">
            {config.label}
          </span>
        )}
      </div>

      {/* Progress Line for active stages */}
      {(ku.status === 'stage1' || ku.status === 'stage2') && (
        <div className="mt-2.5 w-full bg-slate-100 h-1 rounded-full overflow-hidden">
          <div className="h-full bg-indigo-500/50 w-full animate-progress-indeterminate"></div>
        </div>
      )}
    </div>
  );
};

export default KUProgressCard;
