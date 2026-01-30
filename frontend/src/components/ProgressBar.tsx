import React from 'react';

interface ProgressBarProps {
  percent: number;
  showLabel?: boolean;
  height?: 'sm' | 'md' | 'lg';
}

/**
 * ProgressBar component for displaying progress percentage with a visual bar.
 * 
 * Features:
 * - Visual progress bar with percentage fill
 * - Optional percentage label display
 * - Configurable height (sm, md, lg)
 * - Smooth transitions
 * - Styled with Tailwind CSS
 * 
 * Requirements: 4.4
 */
const ProgressBar: React.FC<ProgressBarProps> = ({
  percent,
  showLabel = true,
  height = 'md'
}) => {
  // Clamp percent between 0 and 100
  const clampedPercent = Math.min(Math.max(percent, 0), 100);

  // Height classes
  const heightClasses = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4'
  };

  return (
    <div className="progress-bar w-full">
      {showLabel && (
        <div className="flex justify-between items-center mb-1.5">
          <span className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider">Progress</span>
          <span className="text-xs font-bold text-[var(--accent-primary)]">
            {clampedPercent.toFixed(0)}%
          </span>
        </div>
      )}
      <div className={`w-full bg-slate-100 rounded-full overflow-hidden ${heightClasses[height]}`}>
        <div
          className="h-full bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-secondary)] rounded-full transition-all duration-500 ease-out shadow-[0_0_10px_rgba(99,102,241,0.3)]"
          style={{ width: `${clampedPercent}%` }}
          role="progressbar"
          aria-valuenow={clampedPercent}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
