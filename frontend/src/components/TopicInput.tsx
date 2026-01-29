import React, { useState } from 'react';

interface TopicInputProps {
  onSubmit: (topic: string) => void;
  loading?: boolean;
}

/**
 * TopicInput component for entering a topic and generating a document specification.
 * 
 * Features:
 * - Input field for topic entry
 * - Submit button to trigger spec generation
 * - Loading state during spec generation
 * - Form validation (non-empty topic)
 * 
 * Requirements: 1.3
 */
const TopicInput: React.FC<TopicInputProps> = ({ onSubmit, loading = false }) => {
  const [topic, setTopic] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate topic is not empty
    const trimmedTopic = topic.trim();
    if (!trimmedTopic) {
      return;
    }

    onSubmit(trimmedTopic);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTopic(e.target.value);
  };

  return (
    <div className="topic-input">
      <h2 className="text-xl font-bold mb-4">Generate Document</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="topic-input" className="block text-sm font-medium text-gray-700 mb-2">
            Enter Topic
          </label>
          <input
            id="topic-input"
            type="text"
            value={topic}
            onChange={handleInputChange}
            placeholder="e.g., Introduction to React Hooks"
            disabled={loading}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !topic.trim()}
          className="w-full px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Generating Spec...
            </span>
          ) : (
            'Generate Spec'
          )}
        </button>
      </form>
    </div>
  );
};

export default TopicInput;
