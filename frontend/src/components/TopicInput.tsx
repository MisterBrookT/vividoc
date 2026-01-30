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
    <div className="p-6 border-b border-white/5">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="topic-input"
            className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2"
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
              className="w-full px-4 py-3 bg-zinc-900/50 border border-zinc-800 text-zinc-100 placeholder-zinc-600 rounded-xl focus:outline-none focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/10 transition-all shadow-inner text-sm"
            />
            <div className="absolute inset-0 rounded-xl bg-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || !topic.trim()}
          className="w-full bg-zinc-800 hover:bg-zinc-700 text-zinc-200 hover:text-white border border-white/5 py-2.5 px-4 rounded-xl font-medium transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm shadow-lg hover:shadow-indigo-500/10"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-zinc-400 border-t-zinc-100 rounded-full animate-spin" />
              <span>Generating...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span>Generate Spec</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default TopicInput;
