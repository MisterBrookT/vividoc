import React, { useState, useEffect } from 'react';
import { Settings, Clock } from 'lucide-react';
import toast from 'react-hot-toast';
import TopicInput from './TopicInput';
import ConfigModal from './ConfigModal';
import type { DocumentSpec } from '../types/models';
import { generateSpec, getHistory } from '../api/services';
import type { HistoryItem } from '../api/services';

interface LeftSidebarProps {
  onSpecGenerated: (specId: string, spec: DocumentSpec) => void;
  onSelectHistory: (specId: string) => void;
  configModalOpen: boolean;
  onConfigModalChange: (open: boolean) => void;
  currentSpecId: string | null;
}

const LeftSidebar: React.FC<LeftSidebarProps> = ({
  onSpecGenerated,
  onSelectHistory,
  configModalOpen,
  onConfigModalChange,
  currentSpecId,
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
    <div className="w-68 border-r border-[var(--border-color)] flex flex-col glass-panel relative z-10 backdrop-blur-2xl bg-white/40">
      {/* Header */}
      <div className="p-6 border-b border-[var(--border-color)]">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-2 h-8 bg-[var(--accent-primary)] rounded-full shadow-[0_0_15px_rgba(79,70,229,0.3)]" />
          <h1 className="text-xl font-bold text-[var(--text-primary)] tracking-tight">ViviDoc</h1>
        </div>
        <p className="text-xs text-[var(--text-secondary)] pl-4 font-medium">Interactive Document Generator</p>
      </div>

      {/* Topic Input */}
      <TopicInput onSubmit={handleGenerateSpec} loading={loading} />

      {/* History List */}
      <div className="flex-1 overflow-y-auto px-4 py-4 scrollbar-thin">
        <div className="flex items-center gap-2 px-2 pb-2 mb-2 border-b border-black/5">
          <Clock className="w-4 h-4 text-slate-400" />
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">History</h3>
        </div>

        <div className="flex flex-col gap-2">
          {history.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-sm">
              No history yet
            </div>
          ) : (
            history.map((item) => (
              <button
                key={item.id}
                onClick={() => onSelectHistory(item.id)}
                className={`text-left p-3 rounded-xl transition-all border border-transparent ${currentSpecId === item.id
                  ? 'bg-[var(--accent-primary)] text-white shadow-lg shadow-indigo-500/20'
                  : 'hover:bg-white/50 hover:border-slate-200 text-[var(--text-primary)]'
                  }`}
              >
                <div className="font-medium truncate text-sm mb-0.5">{item.topic}</div>
                <div className={`text-[10px] ${currentSpecId === item.id ? 'text-indigo-100' : 'text-slate-400'}`}>
                  {new Date(item.timestamp).toLocaleString()}
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Config Button */}
      <div className="p-4 border-t border-[var(--border-color)] bg-white/30 backdrop-blur-sm">
        <button
          onClick={() => onConfigModalChange(true)}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-all"
        >
          <Settings className="w-4 h-4" />
          <span>Configuration</span>
        </button>
      </div>

      {/* Config Modal */}
      <ConfigModal isOpen={configModalOpen} onClose={() => onConfigModalChange(false)} />
    </div>
  );
};

export default LeftSidebar;
