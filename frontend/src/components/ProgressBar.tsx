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
    sm: 'h-2',
    md: 'h-4',
    lg: 'h-6'
  };

  return (
    <div className="progress-bar w-full">
      {showLabel && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Progress</span>
          <span className="text-sm font-semibold text-gray-900">
            {clampedPercent.toFixed(0)}%
          </span>
        </div>
      )}
      <div className={`w-full bg-gray-200 rounded-full overflow-hidden ${heightClasses[height]}`}>
        <div
          className="h-full bg-blue-600 rounded-full transition-all duration-300 ease-out"
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
