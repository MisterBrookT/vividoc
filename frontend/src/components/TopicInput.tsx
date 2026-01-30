import React, { useState } from 'react';
import { Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';

interface TopicInputProps {
  onSubmit: (topic: string) => void;
  loading?: boolean;
}

const TopicInput: React.FC<TopicInputProps> = ({ onSubmit, loading = false }) => {
  const [topic, setTopic] = useState('');

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!topic.trim()) {
      toast.error('Please enter a topic');
      return;
    }

    onSubmit(topic.trim());
  };

  return (
    <div className="p-6 border-b border-[var(--border-color)]">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="topic-input"
            className="block text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-2"
          >
            Topic
          </label>
          <div className="relative group">
            <input
              id="topic-input"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Machine Learning Basics"
              disabled={loading}
              className="w-full input-modern text-sm text-[var(--text-primary)] placeholder-slate-400"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || !topic.trim()}
          className="w-full bg-white hover:bg-slate-50 text-[var(--text-primary)] border border-slate-200 py-2.5 px-4 rounded-xl font-medium transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm shadow-sm hover:shadow-md hover:border-slate-300"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-[var(--accent-primary)] border-t-transparent rounded-full animate-spin" />
              <span>Generating...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 text-[var(--accent-primary)]" />
              <span>Generate Spec</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default TopicInput;
