import React, { useState, useEffect } from 'react';
import { Settings } from 'lucide-react';
import toast from 'react-hot-toast';
import TopicInput from './TopicInput';
import ConfigModal from './ConfigModal';
import type { DocumentSpec } from '../types/models';
import { generateSpec, getHistory } from '../api/services';
import type { HistoryItem } from '../api/services';

interface LeftSidebarProps {
  onSpecGenerated: (specId: string, spec: DocumentSpec) => void;
  onSpecGenerationStart?: () => void;
  onSelectHistory: (specId: string) => void;
  configModalOpen: boolean;
  onConfigModalChange: (open: boolean) => void;
  currentSpecId: string | null;
  onToggleSpec: () => void;
  specPanelCollapsed: boolean;
}

const LeftSidebar: React.FC<LeftSidebarProps> = ({
  onSpecGenerated,
  onSpecGenerationStart,
  onSelectHistory,
  configModalOpen,
  onConfigModalChange,
  currentSpecId,
  onToggleSpec,
  specPanelCollapsed,
}) => {
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  const fetchHistory = async () => {
    try {
      const data = await getHistory();
      setHistory(data.history);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [currentSpecId]); // Refresh when spec changes (new generation)

  const handleGenerateSpec = async (topic: string) => {
    setLoading(true);
    if (onSpecGenerationStart) onSpecGenerationStart();

    try {
      const response = await generateSpec(topic);
      onSpecGenerated(response.spec_id, response.spec);
      fetchHistory(); // Refresh history immediately
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        'Failed to generate spec';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-68 h-full border-r border-[var(--border-color)] flex flex-col glass-panel relative z-10 backdrop-blur-2xl bg-white/40">
      {/* Header */}
      <div className="h-16 px-6 border-b border-[var(--border-color)] flex items-center">
        <div className="flex items-center gap-2">
          <div className="w-2 h-8 bg-[var(--accent-primary)] rounded-full shadow-[0_0_15px_rgba(79,70,229,0.3)]" />
          <div>
            <h1 className="text-xl font-bold text-[var(--text-primary)] tracking-tight leading-none">ViviDoc</h1>
            <p className="text-[10px] text-[var(--text-secondary)] font-medium">Interactive Document Generator</p>
          </div>
        </div>
      </div>

      {/* Topic Input */}
      <TopicInput onSubmit={handleGenerateSpec} loading={loading} />

      {/* History List */}
      <div className="flex-1 overflow-y-auto px-4 py-3 scrollbar-thin">
        <div className="flex items-center gap-2 pb-1 ">
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">History</h3>
        </div>

        <div className="flex flex-col gap-1">
          {history.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-sm">
              No history yet
            </div>
          ) : (
            history.map((item) => (
              <div
                key={item.id}
                className={`relative group rounded-xl transition-all border ${currentSpecId === item.id
                  ? 'bg-[var(--accent-primary)] text-white shadow-lg shadow-indigo-500/20 border-transparent'
                  : 'hover:bg-white/50 hover:border-slate-200 border-transparent'
                  }`}
              >
                <button
                  onClick={() => onSelectHistory(item.id)}
                  className="w-full text-left p-2 pr-8"
                >
                  <div className="font-medium truncate text-[13px] mb-0.5">{item.topic}</div>
                  <div className={`text-[10px] ${currentSpecId === item.id ? 'text-indigo-100' : 'text-slate-400'}`}>
                    {new Date(item.timestamp).toLocaleString()}
                  </div>
                </button>

                {/* Toggle Spec Button */}
                {currentSpecId === item.id && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleSpec();
                    }}
                    className="absolute top-2 right-2 p-1 rounded-md hover:bg-white/20 transition-colors"
                    title={specPanelCollapsed ? "Expand Specification" : "Collapse Specification"}
                  >
                    {specPanelCollapsed ? (
                      // Expand icon (>>)
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="m13 17 5-5-5-5" />
                        <path d="m6 17 5-5-5-5" />
                      </svg>
                    ) : (
                      // Collapse icon (<<)
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="m11 17-5-5 5-5" />
                        <path d="m18 17-5-5 5-5" />
                      </svg>
                    )}
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Config Button */}
      <div className="p-3 border-t border-[var(--border-color)] bg-white/30 backdrop-blur-sm">
        <button
          onClick={() => onConfigModalChange(true)}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-all"
        >
          <Settings className="w-4 h-4" />
          <span>Config</span>
        </button>
      </div>

      {/* Config Modal */}
      <ConfigModal isOpen={configModalOpen} onClose={() => onConfigModalChange(false)} />
    </div>
  );
};

export default LeftSidebar;
