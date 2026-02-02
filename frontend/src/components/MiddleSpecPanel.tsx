import React, { useState } from 'react';
import { Play } from 'lucide-react';
import toast from 'react-hot-toast';
import SpecEditor from './SpecEditor';
import type { DocumentSpec } from '../types/models';
import { generateDocument, updateSpec } from '../api/services';

interface MiddleSpecPanelProps {
    spec: DocumentSpec | null;
    onSpecUpdated: (spec: DocumentSpec) => void;
    onGenerateDocument: (jobId: string) => void;
    collapsed: boolean;
    onToggleCollapse: () => void;
}

const MiddleSpecPanel: React.FC<MiddleSpecPanelProps> = ({
    spec,
    onSpecUpdated,
    onGenerateDocument,
    collapsed,
    onToggleCollapse,
}) => {
    const [generating, setGenerating] = useState(false);

    const handleSpecUpdate = async (updatedSpec: DocumentSpec) => {
        try {
            if (!spec?.id) return;

            await updateSpec(spec.id, updatedSpec);
            onSpecUpdated(updatedSpec);
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

        setGenerating(true);
        try {
            const response = await generateDocument(spec.id);
            onGenerateDocument(response.job_id);
        } catch (err: any) {
            const errorMessage =
                err.response?.data?.error ||
                err.response?.data?.detail ||
                'Failed to start document generation';
            toast.error(errorMessage);
        } finally {
            setGenerating(false);
        }
    };

    if (collapsed) {
        return (
            <div className="w-12 border-r border-[var(--border-color)] bg-white/50 backdrop-blur-md flex flex-col items-center py-4 z-10">
                <button
                    onClick={onToggleCollapse}
                    className="p-2 rounded-lg hover:bg-slate-200/50 text-slate-500 transition-colors"
                    title="Expand Spec Panel"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m13 17 5-5-5-5" /><path d="m6 17 5-5-5-5" /></svg>
                </button>
                <div className="mt-8 flex-1 flex flex-col items-center gap-4">
                    <div className="writing-vertical-rl text-slate-400 font-medium tracking-wide text-xs uppercase transform rotate-180">
                        Specification
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="w-[350px] border-r border-[var(--border-color)] bg-white/50 backdrop-blur-md flex flex-col relative z-10 transition-all duration-300">
            {/* Header */}
            <div className="px-6 py-4 flex items-start justify-between border-b border-[var(--border-color)] bg-white/50 backdrop-blur-sm shrink-0">
                {spec ? (
                    <div>
                        <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-1">Specification</h2>
                        <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)]">
                            <span className="bg-[var(--surface-color)] border border-[var(--border-color)] px-2 py-0.5 rounded text-[var(--text-secondary)] font-mono">
                                {spec.knowledge_units.length} unit{spec.knowledge_units.length !== 1 ? 's' : ''}
                            </span>
                            <span>•</span>
                            <span className="truncate max-w-[150px] font-medium">{spec.topic}</span>
                        </div>
                    </div>
                ) : (
                    <h2 className="text-sm font-semibold text-[var(--text-primary)] self-center">Specification</h2>
                )}

                <button
                    onClick={onToggleCollapse}
                    className="p-1.5 rounded-lg hover:bg-slate-200/50 text-slate-400 hover:text-slate-600 transition-colors"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m11 17-5-5 5-5" /><path d="m18 17-5-5 5-5" /></svg>
                </button>
            </div>

            {/* Editor Content */}
            <div className="flex-1 overflow-y-auto px-4 py-4 scrollbar-thin">
                {spec ? (
                    <SpecEditor spec={spec} onUpdate={handleSpecUpdate} />
                ) : (
                    <div className="flex items-center justify-center h-full p-8 text-center text-slate-400">
                        <p className="text-sm">Select a topic from history or create a new one to view specification.</p>
                    </div>
                )}
            </div>

            {/* Generate Document Button */}
            {spec && (
                <div className="p-6 border-t border-[var(--border-color)] bg-white/30 backdrop-blur-sm">
                    <button
                        onClick={handleGenerateDocument}
                        disabled={generating}
                        className="w-full btn-primary py-3 px-4 rounded-xl font-semibold transition-all shadow-lg hover:shadow-indigo-500/25 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm group"
                    >
                        {generating ? (
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

export default MiddleSpecPanel;
