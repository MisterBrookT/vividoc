import React, { useState } from 'react';
import { Play } from 'lucide-react';
import toast from 'react-hot-toast';
import TopicInput from './TopicInput';
import SpecEditor from './SpecEditor';
import type { DocumentSpec } from '../types/models';
import { generateSpec, updateSpec, generateDocument } from '../api/services';

interface LeftSidebarProps {
  spec: DocumentSpec | null;
  onSpecGenerated: (specId: string, spec: DocumentSpec) => void;
  onSpecUpdated: (spec: DocumentSpec) => void;
  onGenerateDocument: (jobId: string) => void;
}

const LeftSidebar: React.FC<LeftSidebarProps> = ({
  spec,
  onSpecGenerated,
  onSpecUpdated,
  onGenerateDocument,
}) => {
  const [loading, setLoading] = useState(false);
  const [generatingDocument, setGeneratingDocument] = useState(false);

  const handleGenerateSpec = async (topic: string) => {
    setLoading(true);

    try {
      const response = await generateSpec(topic);
      onSpecGenerated(response.spec_id, response.spec);
      toast.success('Spec generated successfully');
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

  const handleSpecUpdate = async (updatedSpec: DocumentSpec) => {
    try {
      if (!spec?.id) return;

      await updateSpec(spec.id, updatedSpec);
      onSpecUpdated(updatedSpec);
      toast.success('Spec updated');
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        'Failed to update spec';
      toast.error(errorMessage);
    }
  };

  const handleGenerateDocument = async () => {
    if (!spec?.id) return;

    setGeneratingDocument(true);

    try {
      const response = await generateDocument(spec.id);
      onGenerateDocument(response.job_id);
      toast.success('Document generation started');
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        'Failed to start document generation';
      toast.error(errorMessage);
    } finally {
      setGeneratingDocument(false);
    }
  };

  return (
    <div className="w-80 border-r border-[var(--border-color)] flex flex-col glass-panel relative z-10 backdrop-blur-2xl">
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

      {/* Spec Editor */}
      <div className="flex-1 overflow-y-auto px-2 py-4 scrollbar-thin">
        {spec ? (
          <SpecEditor spec={spec} onUpdate={handleSpecUpdate} />
        ) : (
          <div className="flex items-center justify-center h-full p-8">
            <div className="text-center p-6 rounded-2xl border border-dashed border-slate-200 bg-slate-50/50">
              <div className="w-12 h-12 bg-white rounded-full mx-auto mb-3 flex items-center justify-center shadow-sm">
                <div className="w-6 h-6 border-2 border-slate-300 rounded-sm" />
              </div>
              <p className="text-sm text-[var(--text-secondary)] font-medium">
                Generate a spec to start editing
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Generate Document Button */}
      {spec && (
        <div className="p-6 border-t border-[var(--border-color)] bg-white/50 backdrop-blur-sm">
          <button
            onClick={handleGenerateDocument}
            disabled={generatingDocument}
            className="w-full btn-primary py-3 px-4 rounded-xl font-semibold transition-all shadow-lg hover:shadow-indigo-500/25 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm group"
          >
            {generatingDocument ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current group-hover:translate-x-0.5 transition-transform" />
                <span>Generate Document</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default LeftSidebar;
