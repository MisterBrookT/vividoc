import React, { useState, useEffect } from 'react';
import { Settings } from 'lucide-react';
import ConfigModal from './ConfigModal';
import { getHistory } from '../api/services';
import type { HistoryItem } from '../api/services';

interface LeftSidebarProps {
  onSelectHistory: (specId: string) => void;
  onNewDoc: () => void;
  configModalOpen: boolean;
  onConfigModalChange: (open: boolean) => void;
  currentSpecId: string | null;
}

const LeftSidebar: React.FC<LeftSidebarProps> = ({
  onSelectHistory,
  onNewDoc,
  configModalOpen,
  onConfigModalChange,
  currentSpecId,
}) => {
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
  }, [currentSpecId]);

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

      {/* New Doc Button */}
      <div className="p-4">
        <button
          onClick={onNewDoc}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 btn-primary rounded-xl text-sm font-semibold transition-all"
        >
          <img src="/vividoc-logo.svg" alt="" className="w-5 h-5" />
          <span>New Doc</span>
        </button>
      </div>

      {/* History List */}
      <div className="flex-1 overflow-y-auto px-4 py-1 scrollbar-thin">
        <div className="flex items-center gap-2 pb-1">
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
                className={`relative group rounded-xl transition-all border ${
                  currentSpecId === item.id
                    ? 'bg-slate-100 border-slate-200 shadow-sm'
                    : 'hover:bg-white/50 hover:border-slate-200 border-transparent'
                }`}
              >
                <button
                  onClick={() => onSelectHistory(item.id)}
                  className="w-full text-left p-2 pr-4"
                >
                  <div className="font-medium truncate text-[13px] mb-0.5">{item.topic}</div>
                  <div className={`text-[10px] ${currentSpecId === item.id ? 'text-slate-500' : 'text-slate-400'}`}>
                    {new Date(item.timestamp).toLocaleString()}
                  </div>
                </button>
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

      <ConfigModal isOpen={configModalOpen} onClose={() => onConfigModalChange(false)} />
    </div>
  );
};

export default LeftSidebar;
