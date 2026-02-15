import React, { useState, useEffect } from 'react';
import {
  Download, ChevronRight, FileText, Layout, FileCode,
  Sparkles, Play, Loader2
} from 'lucide-react';
import toast from 'react-hot-toast';
import DocumentViewer from './DocumentViewer';
import { getDocumentHtml, getDocumentDownloadUrl, generateSpec, generateDocument, updateSpec } from '../api/services';
import type { JobStatus, DocumentSpec, KnowledgeUnit } from '../types/models';

interface CenterPanelProps {
  spec: DocumentSpec | null;
  documentId: string | null;
  liveHtml: string | null;
  jobStatus: JobStatus | null;
  isSpecGenerating: boolean;
  onSpecGenerated: (id: string, spec: DocumentSpec) => void;
  onSpecGenerationStart: () => void;
  onSpecUpdated: (spec: DocumentSpec) => void;
  onGenerateDocument: (jobId: string) => void;
}

type ActiveStage = 'topic' | 'spec' | 'doc';

const CenterPanel: React.FC<CenterPanelProps> = ({
  spec,
  documentId,
  liveHtml,
  jobStatus,
  isSpecGenerating,
  onSpecGenerated,
  onSpecGenerationStart,
  onSpecUpdated,
  onGenerateDocument,
}) => {
  const [html, setHtml] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [topic, setTopic] = useState('');
  const [generatingDoc, setGeneratingDoc] = useState(false);

  // Determine active stage
  const getActiveStage = (): ActiveStage => {
    if (documentId || liveHtml || jobStatus?.status === 'running') return 'doc';
    if (spec) return 'spec';
    return 'topic';
  };
  const activeStage = getActiveStage();
  // Allow user to manually switch to spec view
  const [manualStage, setManualStage] = useState<ActiveStage | null>(null);
  const displayStage = manualStage || activeStage;

  // Reset manual stage when active stage or spec changes
  useEffect(() => {
    setManualStage(null);
  }, [activeStage, spec?.id]);

  useEffect(() => {
    if (liveHtml) {
      setHtml(liveHtml);
    } else {
      // When liveHtml is cleared (e.g. switching to a spec with no doc), clear internal html too
      setHtml(null);
    }
  }, [liveHtml]);

  useEffect(() => {
    if (!documentId) {
      if (!liveHtml) setHtml(null);
      setError(null);
      return;
    }
    const fetchHtml = async () => {
      setLoading(true);
      setError(null);
      try {
        const htmlContent = await getDocumentHtml(documentId);
        setHtml(htmlContent);
      } catch (err) {
        console.error('Failed to fetch document HTML:', err);
        setError('Failed to load document');
        toast.error('Failed to load document');
      } finally {
        setLoading(false);
      }
    };
    fetchHtml();
  }, [documentId, liveHtml]);

  // Reset topic input when spec is cleared (new doc)
  useEffect(() => {
    if (!spec) setTopic('');
  }, [spec]);

  const handleDownload = () => {
    if (!documentId) return;
    window.open(getDocumentDownloadUrl(documentId), '_blank');
  };

  const handleGenerateSpec = async () => {
    if (!topic.trim()) {
      toast.error('Please enter a topic');
      return;
    }
    onSpecGenerationStart();
    try {
      const response = await generateSpec(topic.trim());
      onSpecGenerated(response.spec_id, response.spec);
    } catch (err: any) {
      const msg = err.response?.data?.error || err.response?.data?.detail || 'Failed to generate spec';
      toast.error(msg);
    }
  };

  const handleGenerateDocument = async () => {
    if (!spec?.id) return;
    setGeneratingDoc(true);
    try {
      const response = await generateDocument(spec.id);
      onGenerateDocument(response.job_id);
    } catch (err: any) {
      const msg = err.response?.data?.error || err.response?.data?.detail || 'Failed to start generation';
      toast.error(msg);
    } finally {
      setGeneratingDoc(false);
    }
  };

  const handleSpecUpdate = async (updatedSpec: DocumentSpec) => {
    try {
      if (!spec?.id) return;
      await updateSpec(spec.id, updatedSpec);
      onSpecUpdated(updatedSpec);
    } catch (err: any) {
      const msg = err.response?.data?.error || err.response?.data?.detail || 'Failed to update spec';
      toast.error(msg);
    }
  };


  const isRunning = jobStatus?.status === 'running';

  const getStatusText = () => {
    if (!jobStatus) return 'Ready';
    if (jobStatus.status === 'failed') return 'Generation Failed';
    if (jobStatus.status === 'completed') return 'Done';
    const { phase, ku_progress } = jobStatus.progress;
    if (phase === 'planning') return 'Generating skeleton...';
    if (phase === 'executing') {
      const processing = ku_progress?.filter(k => k.status === 'stage1' || k.status === 'stage2') || [];
      if (processing[0]) {
        const idx = ku_progress.findIndex(k => k.ku_id === processing[0].ku_id);
        return `Generating KU ${idx + 1}...`;
      }
      return 'Generating content...';
    }
    if (phase === 'evaluating') return 'Refining...';
    return 'Initializing...';
  };

  const steps = [
    {
      id: 'topic' as const,
      label: 'Topic',
      icon: Layout,
      active: true,
      current: activeStage === 'topic',
    },
    {
      id: 'spec' as const,
      label: 'Spec',
      icon: FileText,
      active: !!spec,
      current: activeStage === 'spec',
    },
    {
      id: 'doc' as const,
      label: 'Doc',
      icon: FileCode,
      active: !!documentId || !!liveHtml || isRunning,
      current: activeStage === 'doc',
    },
  ];

  return (
    <div className="flex-1 h-full flex flex-col relative z-0">
      {/* Header */}
      <div className="h-16 flex-shrink-0 px-6 flex items-center justify-between bg-[var(--bg-panel)] backdrop-blur-sm border-b border-[var(--border-color)] z-20">
        <div className="flex items-center gap-1">
          {steps.map((step, index) => (
            <React.Fragment key={step.id}>
              <button
                onClick={() => {
                  if (step.active) setManualStage(step.id);
                }}
                disabled={!step.active}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all ${
                  step.active
                    ? 'text-[var(--text-primary)] hover:bg-white/60 cursor-pointer'
                    : 'text-slate-300 cursor-not-allowed'
                } ${displayStage === step.id ? 'bg-white shadow-sm ring-1 ring-slate-200/50' : ''}`}
              >
                <step.icon className={`w-4 h-4 ${step.active ? 'text-[var(--accent-primary)]' : 'text-slate-300'}`} />
                <span className={`text-sm font-medium ${step.active ? 'text-slate-700' : 'text-slate-400'}`}>{step.label}</span>
              </button>
              {index < steps.length - 1 && (
                <ChevronRight className={`w-4 h-4 ${steps[index + 1].active ? 'text-slate-400' : 'text-slate-200'}`} />
              )}
            </React.Fragment>
          ))}
        </div>

        <div className="flex items-center gap-4">
          {isRunning && (
            <div className="flex items-center gap-2 px-3 py-1 bg-indigo-50/50 rounded-full border border-indigo-100">
              <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse" />
              <span className="text-xs font-medium text-indigo-600 truncate max-w-[150px]">{getStatusText()}</span>
            </div>
          )}
          {documentId && (
            <button
              onClick={handleDownload}
              disabled={loading || !!error}
              className="inline-flex items-center gap-2 px-4 py-2 btn-primary rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm shadow-lg hover:shadow-indigo-500/25 active:scale-95"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </button>
          )}
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden">
        {displayStage === 'topic' && (
          <TopicView
            topic={topic}
            onTopicChange={setTopic}
            onGenerate={handleGenerateSpec}
            isGenerating={isSpecGenerating}
          />
        )}
        {displayStage === 'spec' && spec && (
          <SpecView
            spec={spec}
            onSpecUpdated={handleSpecUpdate}
            onGenerateDocument={handleGenerateDocument}
            generatingDoc={generatingDoc}
          />
        )}
        {displayStage === 'doc' && (
          <DocumentViewer
            html={html}
            loading={loading && !html}
            error={error}
          />
        )}
      </div>
    </div>
  );
};

/* ---- Topic Input View ---- */
interface TopicViewProps {
  topic: string;
  onTopicChange: (t: string) => void;
  onGenerate: () => void;
  isGenerating: boolean;
}

const TopicView: React.FC<TopicViewProps> = ({ topic, onTopicChange, onGenerate, isGenerating }) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onGenerate();
    }
  };

  return (
    <div className="w-full h-full flex items-center justify-center bg-[var(--bg-app)]">
      <div className="w-full max-w-lg px-8">
        <div className="text-center mb-8">
          <img src="/vividoc-logo.svg" alt="ViviDoc" className="w-16 h-16 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-[var(--text-primary)] mb-2">What would you like to explore?</h2>
          <p className="text-sm text-[var(--text-secondary)]">Enter a topic and we'll generate an interactive document specification.</p>
        </div>
        <div className="space-y-4">
          <input
            type="text"
            value={topic}
            onChange={(e) => onTopicChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="e.g., What is Fourier Transform?"
            disabled={isGenerating}
            className="w-full input-modern text-base py-3 px-5 rounded-xl"
          />
          <button
            onClick={onGenerate}
            disabled={isGenerating || !topic.trim()}
            className="w-full btn-primary py-3 px-4 rounded-xl font-semibold flex items-center justify-center gap-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate Spec</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

/* ---- Spec View ---- */
interface SpecViewProps {
  spec: DocumentSpec;
  onSpecUpdated: (spec: DocumentSpec) => void;
  onGenerateDocument: () => void;
  generatingDoc: boolean;
}

const SpecView: React.FC<SpecViewProps> = ({ spec, onSpecUpdated, onGenerateDocument, generatingDoc }) => {
  const [editingKuId, setEditingKuId] = useState<string | null>(null);

  const handleKuFieldChange = (kuId: string, field: keyof KnowledgeUnit, value: string) => {
    const updated = {
      ...spec,
      knowledge_units: spec.knowledge_units.map(ku =>
        ku.id === kuId ? { ...ku, [field]: value } : ku
      ),
    };
    onSpecUpdated(updated);
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-y-auto">
        <div className="px-10 py-8">
          {/* Topic Header */}
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-[var(--text-primary)] mb-1">{spec.topic}</h2>
            <p className="text-sm text-[var(--text-secondary)]">
              {spec.knowledge_units.length} knowledge unit{spec.knowledge_units.length !== 1 ? 's' : ''}
            </p>
          </div>

          {/* KU List */}
          <div className="space-y-4">
            {spec.knowledge_units.map((ku, index) => {
              const isEditing = editingKuId === ku.id;
              return (
                <div
                  key={ku.id}
                  className={`bg-white rounded-xl border p-5 transition-all relative overflow-hidden cursor-pointer ${
                    isEditing
                      ? 'border-[var(--accent-primary)] shadow-md ring-2 ring-[var(--accent-primary)]/10'
                      : 'border-[var(--border-color)] hover:shadow-md'
                  }`}
                  onClick={() => !isEditing && setEditingKuId(ku.id)}
                >
                  <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-indigo-500 to-purple-500 opacity-80" />
                  <div className="pl-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-bold text-[var(--accent-primary)] uppercase tracking-wider">
                        KU {index + 1}
                      </span>
                      {isEditing && (
                        <button
                          onClick={(e) => { e.stopPropagation(); setEditingKuId(null); }}
                          className="text-xs text-slate-500 hover:text-slate-700 px-2 py-0.5 rounded hover:bg-slate-100 transition-colors"
                        >
                          Done
                        </button>
                      )}
                    </div>

                    {isEditing ? (
                      <div className="space-y-3" onClick={(e) => e.stopPropagation()}>
                        <div>
                          <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">Title</label>
                          <input
                            type="text"
                            value={ku.title}
                            onChange={(e) => handleKuFieldChange(ku.id, 'title', e.target.value)}
                            className="w-full text-sm font-semibold text-[var(--text-primary)] bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-[var(--accent-primary)] focus:ring-2 focus:ring-[var(--accent-primary)]/10 transition-all"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">Description</label>
                          <textarea
                            value={ku.description}
                            onChange={(e) => handleKuFieldChange(ku.id, 'description', e.target.value)}
                            rows={3}
                            className="w-full text-sm text-[var(--text-secondary)] bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-[var(--accent-primary)] focus:ring-2 focus:ring-[var(--accent-primary)]/10 transition-all resize-none leading-relaxed"
                          />
                        </div>
                        <div>
                          <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">Interaction</label>
                          <textarea
                            value={ku.interaction_description || ''}
                            onChange={(e) => handleKuFieldChange(ku.id, 'interaction_description', e.target.value)}
                            rows={3}
                            placeholder="Describe the interactive elements..."
                            className="w-full text-sm text-[var(--text-secondary)] bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-[var(--accent-primary)] focus:ring-2 focus:ring-[var(--accent-primary)]/10 transition-all resize-none leading-relaxed placeholder:text-slate-400"
                          />
                        </div>
                      </div>
                    ) : (
                      <>
                        <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-2">{ku.title}</h3>
                        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{ku.description}</p>
                        {ku.interaction_description && (
                          <div className="mt-3 pt-3 border-t border-slate-100">
                            <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Interaction</span>
                            <p className="text-sm text-[var(--text-secondary)] mt-1 leading-relaxed">{ku.interaction_description}</p>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Generate Document Footer */}
      <div className="flex-shrink-0 p-4 border-t border-[var(--border-color)] bg-white/30 backdrop-blur-sm">
        <div className="px-6">
          <button
            onClick={onGenerateDocument}
            disabled={generatingDoc}
            className="w-full btn-primary py-3 px-4 rounded-xl font-semibold flex items-center justify-center gap-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed group"
          >
            {generatingDoc ? (
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
      </div>
    </div>
  );
};

export default CenterPanel;
