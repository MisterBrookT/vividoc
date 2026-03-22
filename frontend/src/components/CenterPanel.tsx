import React, { useState, useEffect } from 'react';
import {
  Download, ChevronRight, FileText, Layout, FileCode,
  Sparkles, Loader2, Palette
} from 'lucide-react';
import toast from 'react-hot-toast';
import DocumentViewer from './DocumentViewer';
import StyleView from './StyleView';
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

type ActiveStage = 'topic' | 'spec' | 'style' | 'doc';

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
  // When spec is generating, force show spec stage with loading
  const displayStage = isSpecGenerating ? 'spec' : (manualStage || activeStage);

  // Reset manual stage when active stage or spec changes
  useEffect(() => {
    setManualStage(null);
    setStyleVisited(false);
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
    if (documentId) {
      window.open(getDocumentDownloadUrl(documentId), '_blank');
    } else if (html) {
      const blob = new Blob([html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${spec?.topic || 'document'}.html`;
      a.click();
      URL.revokeObjectURL(url);
    }
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

  // Track whether user has entered style stage
  const [styleVisited, setStyleVisited] = useState(false);

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
      active: !!spec || isSpecGenerating,
      current: activeStage === 'spec',
    },
    {
      id: 'style' as const,
      label: 'Style',
      icon: Palette,
      active: styleVisited || displayStage === 'style' || !!documentId || !!liveHtml || isRunning,
      current: activeStage === 'style',
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
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all ${step.active
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
          {(documentId || html) && (
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
            onGenerateDocument={() => { setStyleVisited(true); setManualStage('style'); }}
            generatingDoc={generatingDoc}
          />
        )}
        {displayStage === 'spec' && !spec && isSpecGenerating && (
          <div className="w-full h-full flex items-center justify-center">
            <div className="flex flex-col items-center gap-4">
              <div className="relative">
                <div className="w-16 h-16 rounded-2xl bg-indigo-50 flex items-center justify-center">
                  <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
                </div>
              </div>
              <div className="text-center">
                <p className="text-base font-semibold text-slate-700">Generating Spec</p>
                <p className="text-sm text-slate-400 mt-1">Analyzing your topic and creating knowledge units...</p>
              </div>
            </div>
          </div>
        )}
        {displayStage === 'style' && spec?.id && (
          <StyleView
            specId={spec.id}
            onStyleSaved={() => {
              handleGenerateDocument();
            }}
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
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      onGenerate();
    }
  };

  return (
    <div className="w-full h-full flex items-center justify-center bg-[var(--bg-app)]">
      <div className="w-full max-w-lg px-8">
        <div className="text-center mb-8">
          <img src="/vivi-cat-transparent.png" alt="Vivi" className="w-48 h-48 mx-auto mb-6 object-contain drop-shadow-md" />
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

  const handleKuFieldChange = (kuId: string, field: keyof KnowledgeUnit, value: any) => {
    const updated = {
      ...spec,
      knowledge_units: spec.knowledge_units.map(ku =>
        ku.id === kuId ? { ...ku, [field]: value } : ku
      ),
    };
    onSpecUpdated(updated);
  };

  const handleInteractionSpecChange = (kuId: string, specField: string, value: any) => {
    const updated = {
      ...spec,
      knowledge_units: spec.knowledge_units.map(ku => {
        if (ku.id !== kuId) return ku;
        const currentSpec = ku.interaction_spec || { state: {}, render: [], transition: [], constraint: null };
        return {
          ...ku,
          interaction_spec: {
            state: currentSpec.state,
            render: currentSpec.render,
            transition: currentSpec.transition,
            constraint: currentSpec.constraint,
            [specField]: value,
          },
        };
      }),
    };
    onSpecUpdated(updated);
  };

  const handleDeleteKU = (kuId: string) => {
    const updated = {
      ...spec,
      knowledge_units: spec.knowledge_units.filter(ku => ku.id !== kuId),
    };
    onSpecUpdated(updated);
    if (editingKuId === kuId) setEditingKuId(null);
  };

  const handleAddKU = (afterIndex: number) => {
    const newId = `ku_${Date.now()}`;
    const newKU: KnowledgeUnit = {
      id: newId,
      title: 'New Knowledge Unit',
      description: '',
      interaction_spec: { state: {}, render: [], transition: [], constraint: null },
    };
    const units = [...spec.knowledge_units];
    units.splice(afterIndex + 1, 0, newKU);
    const updated = { ...spec, knowledge_units: units };
    onSpecUpdated(updated);
    setEditingKuId(newId);
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
                  className={`bg-white rounded-xl border p-5 transition-all relative overflow-hidden ${isEditing
                    ? 'border-[var(--accent-primary)] shadow-md ring-2 ring-[var(--accent-primary)]/10'
                    : 'border-[var(--border-color)] hover:shadow-md'
                    }`}
                >
                  <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-indigo-500 to-purple-500 opacity-80" />
                  <div className="pl-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-bold text-[var(--accent-primary)] uppercase tracking-wider">
                        KU {index + 1}
                      </span>
                      <div className="flex items-center gap-1">
                        {isEditing ? (
                          <button
                            onClick={() => setEditingKuId(null)}
                            className="text-[11px] text-slate-500 hover:text-slate-700 px-2 py-0.5 rounded hover:bg-slate-100 transition-colors font-medium"
                          >
                            Done
                          </button>
                        ) : (
                          <>
                            <button
                              onClick={() => setEditingKuId(ku.id)}
                              className="text-[11px] text-indigo-500 hover:text-indigo-700 px-1.5 py-0.5 rounded hover:bg-indigo-50 transition-colors font-medium"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => handleDeleteKU(ku.id)}
                              className="text-[11px] text-red-400 hover:text-red-600 px-1.5 py-0.5 rounded hover:bg-red-50 transition-colors font-medium"
                            >
                              Delete
                            </button>
                            <button
                              onClick={() => handleAddKU(index)}
                              className="text-[11px] text-emerald-500 hover:text-emerald-700 px-1.5 py-0.5 rounded hover:bg-emerald-50 transition-colors font-medium"
                            >
                              + Add
                            </button>
                          </>
                        )}
                      </div>
                    </div>

                    {isEditing ? (
                      <div className="space-y-3">
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
                        <div className="border-t border-slate-100 pt-3">
                          <label className="text-[10px] font-semibold text-indigo-500 uppercase tracking-wider block mb-2">Interaction Spec (S, R, T, C)</label>
                          <div className="space-y-2">
                            <div>
                              <label className="text-[10px] text-slate-400 block mb-0.5">State (JSON)</label>
                              <textarea
                                value={JSON.stringify(ku.interaction_spec?.state || {}, null, 2)}
                                onChange={(e) => { try { handleInteractionSpecChange(ku.id, 'state', JSON.parse(e.target.value)); } catch { } }}
                                rows={4}
                                className="w-full text-xs font-mono text-[var(--text-secondary)] bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-[var(--accent-primary)] transition-all resize-none"
                              />
                            </div>
                            <div>
                              <label className="text-[10px] text-slate-400 block mb-0.5">Render (one per line)</label>
                              <textarea
                                value={(ku.interaction_spec?.render || []).join('\n')}
                                onChange={(e) => handleInteractionSpecChange(ku.id, 'render', e.target.value.split('\n').filter(Boolean))}
                                rows={2}
                                className="w-full text-xs text-[var(--text-secondary)] bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-[var(--accent-primary)] transition-all resize-none"
                              />
                            </div>
                            <div>
                              <label className="text-[10px] text-slate-400 block mb-0.5">Transition (one per line)</label>
                              <textarea
                                value={(ku.interaction_spec?.transition || []).join('\n')}
                                onChange={(e) => handleInteractionSpecChange(ku.id, 'transition', e.target.value.split('\n').filter(Boolean))}
                                rows={2}
                                className="w-full text-xs text-[var(--text-secondary)] bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-[var(--accent-primary)] transition-all resize-none"
                              />
                            </div>
                            <div>
                              <label className="text-[10px] text-slate-400 block mb-0.5">Constraint</label>
                              <input
                                type="text"
                                value={ku.interaction_spec?.constraint || ''}
                                onChange={(e) => handleInteractionSpecChange(ku.id, 'constraint', e.target.value || null)}
                                placeholder="Pedagogical invariant..."
                                className="w-full text-xs text-[var(--text-secondary)] bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-[var(--accent-primary)] transition-all placeholder:text-slate-400"
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <>
                        <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-2">{ku.title}</h3>
                        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{ku.description}</p>
                        {ku.interaction_spec && (ku.interaction_spec.render?.length > 0 || ku.interaction_spec.transition?.length > 0) && (
                          <div className="mt-3 pt-3 border-t border-slate-100 space-y-2">
                            {Object.keys(ku.interaction_spec.state || {}).length > 0 && (
                              <div>
                                <span className="text-[10px] font-semibold text-indigo-500 uppercase tracking-wider">State</span>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {Object.entries(ku.interaction_spec.state).map(([name, def]: [string, any]) => (
                                    <span key={name} className="text-[10px] px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded-full font-mono">
                                      {name}{def.derived ? ` = ${def.derived}` : def.control ? ` (${def.control})` : ''}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                            {ku.interaction_spec.render?.length > 0 && (
                              <div>
                                <span className="text-[10px] font-semibold text-emerald-500 uppercase tracking-wider">Render</span>
                                <ul className="mt-1 space-y-0.5">
                                  {ku.interaction_spec.render.map((r, i) => (
                                    <li key={i} className="text-xs text-[var(--text-secondary)] leading-relaxed">• {r}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {ku.interaction_spec.transition?.length > 0 && (
                              <div>
                                <span className="text-[10px] font-semibold text-amber-500 uppercase tracking-wider">Transition</span>
                                <ul className="mt-1 space-y-0.5">
                                  {ku.interaction_spec.transition.map((t, i) => (
                                    <li key={i} className="text-xs text-[var(--text-secondary)] leading-relaxed">→ {t}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {ku.interaction_spec.constraint && (
                              <div>
                                <span className="text-[10px] font-semibold text-rose-500 uppercase tracking-wider">Constraint</span>
                                <p className="text-xs text-[var(--text-secondary)] mt-0.5 italic">{ku.interaction_spec.constraint}</p>
                              </div>
                            )}
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

      {/* Next: Style Preferences */}
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
                <Palette className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                <span>Next: Style Preferences</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CenterPanel;
