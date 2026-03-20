import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Sparkles, AlertCircle, CheckCircle2, Loader2, FileText } from 'lucide-react';
import Markdown from 'react-markdown';
import type { JobStatus, DocumentSpec } from '../types/models';
import { streamChat, getChatHistory, saveChatHistory } from '../api/services';

/* Cute Vivi avatar SVG — a small friendly bot face */
const ViviAvatar: React.FC<{ className?: string }> = ({ className }) => (
    <svg className={className} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="16" cy="16" r="15" fill="url(#vivi-grad)" stroke="#818cf8" strokeWidth="1" />
        <ellipse cx="11" cy="14" rx="2.2" ry="2.5" fill="white" />
        <ellipse cx="21" cy="14" rx="2.2" ry="2.5" fill="white" />
        <circle cx="11" cy="14.5" r="1.2" fill="#312e81" />
        <circle cx="21" cy="14.5" r="1.2" fill="#312e81" />
        <circle cx="11.6" cy="13.8" r="0.5" fill="white" />
        <circle cx="21.6" cy="13.8" r="0.5" fill="white" />
        <path d="M12 20.5Q16 23.5 20 20.5" stroke="#312e81" strokeWidth="1.2" strokeLinecap="round" fill="none" />
        <ellipse cx="7.5" cy="18" rx="1.8" ry="1" fill="#c7d2fe" opacity="0.6" />
        <ellipse cx="24.5" cy="18" rx="1.8" ry="1" fill="#c7d2fe" opacity="0.6" />
        <defs>
            <linearGradient id="vivi-grad" x1="0" y1="0" x2="32" y2="32">
                <stop offset="0%" stopColor="#e0e7ff" />
                <stop offset="100%" stopColor="#c7d2fe" />
            </linearGradient>
        </defs>
    </svg>
);

interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: number;
    type?: 'text' | 'spec-notification' | 'progress' | 'edit-status';
    metadata?: any;
}

interface RightChatPanelProps {
    jobStatus: JobStatus | null;
    onSendMessage: (message: string) => void;
    isGeneratingSpec: boolean;
    spec: DocumentSpec | null;
    specJustGenerated: boolean;
    onSpecJustGeneratedConsumed: () => void;
    onHtmlUpdated?: (html: string) => void;
    onSpecUpdated?: (spec: DocumentSpec) => void;
    activeStage?: 'topic' | 'spec' | 'doc';
}

const RightChatPanel: React.FC<RightChatPanelProps> = ({
    jobStatus,
    onSendMessage,
    isGeneratingSpec,
    spec,
    specJustGenerated,
    onSpecJustGeneratedConsumed,
    onHtmlUpdated,
    onSpecUpdated,
    activeStage = 'doc',
}) => {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: 'welcome',
            role: 'assistant',
            content: "Hi! I'm Vivi, your AI assistant. I can help you modify the generated document. What would you like to do?",
            timestamp: Date.now(),
        },
    ]);
    const [input, setInput] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const progressMsgIdRef = useRef<string | null>(null);
    const prevSpecIdRef = useRef<string | null>(null);
    const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    const defaultMessages: Message[] = [
        {
            id: 'welcome',
            role: 'assistant',
            content: "Hi! I'm Vivi, your AI assistant. I can help you modify the generated document. What would you like to do?",
            timestamp: Date.now(),
        },
    ];

    // Save current messages to backend (debounced)
    const saveMessages = useCallback((specId: string, msgs: Message[]) => {
        if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
        saveTimerRef.current = setTimeout(() => {
            saveChatHistory(specId, msgs).catch(() => {});
        }, 500);
    }, []);

    // When spec changes: save old, load new
    useEffect(() => {
        const prevId = prevSpecIdRef.current;
        const newId = spec?.id || null;

        if (prevId === newId) return;

        // Save current messages for the old spec
        if (prevId && messages.length > 1) {
            saveChatHistory(prevId, messages).catch(() => {});
        }

        // Load messages for the new spec
        if (newId) {
            getChatHistory(newId).then((saved) => {
                if (saved && saved.length > 0) {
                    setMessages(saved);
                } else {
                    setMessages(defaultMessages);
                }
            }).catch(() => {
                setMessages(defaultMessages);
            });
        } else {
            setMessages(defaultMessages);
        }

        prevSpecIdRef.current = newId;
    }, [spec?.id]);

    useEffect(() => {
        if (specJustGenerated && spec) {
            const newMessage: Message = {
                id: `spec-${spec.id}`,
                role: 'assistant',
                content: 'Specification generated!',
                timestamp: Date.now(),
                type: 'spec-notification',
                metadata: { specId: spec.id, topic: spec.topic, unitCount: spec.knowledge_units.length }
            };
            setMessages((prev) => [...prev, newMessage]);
            onSpecJustGeneratedConsumed();
        }
    }, [specJustGenerated, spec, onSpecJustGeneratedConsumed]);

    useEffect(() => {
        if (!jobStatus) return;
        const isRunning = jobStatus.status === 'running';
        const isFailed = jobStatus.status === 'failed';
        const isCompleted = jobStatus.status === 'completed';
        if (!isRunning && !isFailed && !isCompleted) return;

        if (isRunning && !progressMsgIdRef.current) {
            const msgId = `progress-${jobStatus.job_id}`;
            progressMsgIdRef.current = msgId;
            setMessages((prev) => [...prev, {
                id: msgId, role: 'assistant', content: '', timestamp: Date.now(),
                type: 'progress', metadata: { jobStatus },
            }]);
        } else if (progressMsgIdRef.current) {
            setMessages((prev) => prev.map(m =>
                m.id === progressMsgIdRef.current ? { ...m, metadata: { jobStatus } } : m
            ));
        }
        if (isCompleted || isFailed) progressMsgIdRef.current = null;
    }, [jobStatus]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, [messages, isStreaming]);

    // Persist messages when they change
    useEffect(() => {
        if (spec?.id && messages.length > 1) {
            saveMessages(spec.id, messages);
        }
    }, [messages, spec?.id, saveMessages]);

    const handleSend = useCallback(async () => {
        if (!input.trim() || isStreaming) return;
        const userMsg = input.trim();
        setInput('');

        setMessages((prev) => [...prev, {
            id: Date.now().toString(), role: 'user', content: userMsg, timestamp: Date.now(),
        }]);
        onSendMessage(userMsg);

        if (spec?.id) {
            const assistantMsgId = `assistant-${Date.now()}`;
            setMessages((prev) => [...prev, {
                id: assistantMsgId, role: 'assistant', content: '', timestamp: Date.now(),
                type: 'text', metadata: { editMode: false, editDone: false, description: '' },
            }]);
            setIsStreaming(true);

            let isEditMode = false;
            let rawContent = '';

            try {
                const chatStage = activeStage === 'spec' ? 'spec' : 'doc';
                await streamChat(spec.id, userMsg, (event) => {
                    if (event.type === 'edit_mode_start') {
                        isEditMode = true;
                        setMessages((prev) => prev.map(m =>
                            m.id === assistantMsgId
                                ? { ...m, type: 'edit-status', metadata: { editMode: true, editDone: false, description: '' } }
                                : m
                        ));
                    } else if (event.type === 'token' && event.content) {
                        rawContent += event.content;
                        if (isEditMode) {
                            const cleaned = rawContent.replace('[EDIT_MODE]', '').replace('[SPEC_EDIT]', '').trim();
                            const editBlockStart = Math.max(cleaned.indexOf('```edit'), cleaned.indexOf('```spec_json'));
                            const desc = editBlockStart > 0
                                ? cleaned.substring(0, editBlockStart).trim()
                                : cleaned.replace(/```[\s\S]*$/, '').trim();
                            setMessages((prev) => prev.map(m =>
                                m.id === assistantMsgId ? { ...m, metadata: { ...m.metadata, description: desc } } : m
                            ));
                        } else {
                            setMessages((prev) => prev.map(m =>
                                m.id === assistantMsgId ? { ...m, content: rawContent } : m
                            ));
                        }
                    } else if (event.type === 'html_updated' && event.html) {
                        setMessages((prev) => prev.map(m =>
                            m.id === assistantMsgId ? { ...m, metadata: { ...m.metadata, editDone: true } } : m
                        ));
                        onHtmlUpdated?.(event.html);
                    } else if (event.type === 'spec_updated' && event.spec) {
                        setMessages((prev) => prev.map(m =>
                            m.id === assistantMsgId ? { ...m, metadata: { ...m.metadata, editDone: true } } : m
                        ));
                        onSpecUpdated?.(event.spec as DocumentSpec);
                    } else if (event.type === 'error') {
                        setMessages((prev) => prev.map(m =>
                            m.id === assistantMsgId
                                ? { ...m, type: 'text', content: `⚠️ Error: ${event.content}`, metadata: { editMode: false } }
                                : m
                        ));
                    }
                }, chatStage);
            } catch (err: any) {
                setMessages((prev) => prev.map(m =>
                    m.id === assistantMsgId
                        ? { ...m, type: 'text', content: `Failed to get response: ${err.message}`, metadata: { editMode: false } }
                        : m
                ));
            } finally {
                setIsStreaming(false);
            }
        }
    }, [input, isStreaming, spec, onSendMessage, onHtmlUpdated, onSpecUpdated, activeStage]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); handleSend(); }
    };

    const renderEditStatusCard = (msg: Message) => {
        const { editDone, description } = msg.metadata || {};
        return (
            <div className="flex flex-col items-start">
                <div className="flex items-start gap-2 max-w-[95%]">
                    <ViviAvatar className="w-6 h-6 flex-shrink-0 mt-0.5" />
                    <div>
                        <span className="text-[10px] font-medium text-indigo-500 mb-1 block">Vivi</span>
                        <div className="bg-white border border-indigo-100 rounded-xl shadow-sm text-sm overflow-hidden">
                            <div className="px-3 py-2 border-b border-indigo-50 flex items-center justify-between gap-4">
                                <div className="flex items-center gap-1.5 text-xs font-semibold text-indigo-600">
                                    {editDone ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> : <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                                    <span>{editDone ? 'Document Updated' : 'Editing Document...'}</span>
                                </div>
                                <span className="text-[10px] text-slate-400">{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                            </div>
                            {description && (
                                <div className="px-3 py-2">
                                    <p className="text-xs text-slate-600 leading-relaxed">{description}</p>
                                </div>
                            )}
                            {!editDone && (
                                <div className="px-3 pb-2">
                                    <div className="h-1 w-full bg-slate-100 rounded-full overflow-hidden">
                                        <div className="h-full bg-indigo-500 rounded-full animate-pulse" style={{ width: '60%' }} />
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const renderProgressCard = (js: JobStatus) => {
        const isRunning = js.status === 'running';
        const { phase, ku_progress, overall_percent } = js.progress;
        const cappedPercent = Math.min(Math.round(overall_percent || 0), 100);
        return (
            <div className="p-3 bg-white/80 backdrop-blur-sm rounded-xl border border-indigo-100 shadow-sm">
                <div className="flex items-center gap-2 mb-2">
                    {isRunning ? (
                        <div className="relative flex h-2.5 w-2.5">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-indigo-500"></span>
                        </div>
                    ) : js.status === 'failed' ? (
                        <AlertCircle className="w-3.5 h-3.5 text-red-500" />
                    ) : (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                    )}
                    <span className="text-xs font-semibold text-slate-700">
                        {isRunning ? 'Generating Document...' : js.status === 'failed' ? 'Generation Failed' : 'Completed'}
                    </span>
                </div>
                <div className="space-y-2">
                    <div className="flex justify-between text-[10px] text-slate-500 mb-0.5">
                        <span>Progress</span><span>{cappedPercent}%</span>
                    </div>
                    <div className="h-1 w-full bg-slate-100 rounded-full overflow-hidden">
                        <div className="h-full bg-indigo-500 rounded-full transition-all duration-500 ease-out" style={{ width: `${cappedPercent}%` }} />
                    </div>
                    <div className="mt-2 space-y-1.5">
                        <div className={`flex items-center gap-1.5 text-[10px] ${phase === 'executing' && isRunning ? 'text-indigo-600 font-medium' : phase === 'evaluating' || !isRunning ? 'text-emerald-600' : 'text-slate-400'}`}>
                            {phase === 'executing' && isRunning ? (
                                <div className="w-1 h-1 rounded-full bg-indigo-500 animate-pulse" />
                            ) : phase === 'evaluating' || !isRunning ? (
                                <CheckCircle2 className="w-2.5 h-2.5 text-emerald-500" />
                            ) : (
                                <div className="w-1 h-1 rounded-full bg-slate-300" />
                            )}
                            Generating Content
                        </div>
                        {phase === 'executing' && ku_progress && (
                            <div className="ml-2.5 pl-2 border-l border-indigo-100 space-y-1 mt-0.5">
                                {ku_progress.filter(k => k.status === 'stage1' || k.status === 'stage2').map(k => (
                                    <div key={k.ku_id} className="text-[10px] text-indigo-500 flex items-center gap-1">
                                        <Loader2 className="w-2 h-2 animate-spin" />
                                        <span className="truncate max-w-[160px] leading-tight">{k.title || 'Processing unit...'}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                        <div className={`flex items-center gap-1.5 text-[10px] ${phase === 'evaluating' && isRunning ? 'text-indigo-600 font-medium' : !isRunning && js.status === 'completed' ? 'text-emerald-600' : 'text-slate-400'}`}>
                            {phase === 'evaluating' && isRunning ? (
                                <div className="w-1 h-1 rounded-full bg-indigo-500 animate-pulse" />
                            ) : !isRunning && js.status === 'completed' ? (
                                <CheckCircle2 className="w-2.5 h-2.5 text-emerald-500" />
                            ) : (
                                <div className="w-1 h-1 rounded-full bg-slate-300" />
                            )}
                            Refining & Finalizing
                        </div>
                        {phase === 'evaluating' && isRunning && (
                            <div className="ml-2.5 pl-2 border-l border-indigo-100 space-y-1 mt-0.5">
                                <div className="text-[10px] text-indigo-500 flex items-center gap-1">
                                    <Loader2 className="w-2 h-2 animate-spin" />
                                    <span className="leading-tight">Evaluating document quality...</span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        );
    };

    const isAnyJobRunning = jobStatus?.status === 'running' || isGeneratingSpec || isStreaming;

    return (
        <div className="w-[300px] h-full bg-white/60 backdrop-blur-xl border-l border-[var(--border-color)] flex flex-col relative z-20 transition-all duration-300">
            {/* Header */}
            <div className="flex-shrink-0 h-16 px-4 border-b border-[var(--border-color)] flex items-center bg-white/40">
                <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-[var(--accent-primary)]" />
                    <h2 className="text-sm font-semibold text-slate-700">AI Assistant</h2>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent p-3 space-y-3">
                {messages.map((msg) => {
                    if (msg.type === 'spec-notification') {
                        return (
                            <div key={msg.id} className="flex items-start gap-2">
                                <ViviAvatar className="w-6 h-6 flex-shrink-0 mt-0.5" />
                                <div>
                                    <span className="text-[10px] font-medium text-indigo-500 mb-1 block">Vivi</span>
                                    <div className="max-w-full bg-white border border-slate-200 rounded-xl shadow-sm text-sm overflow-hidden">
                                        <div className="px-3 py-2 border-b border-slate-100 flex items-center justify-between gap-4">
                                            <div className="flex items-center gap-1.5 text-xs font-semibold text-indigo-600">
                                                <FileText className="w-3.5 h-3.5" />
                                                <span>Spec Generated</span>
                                            </div>
                                            <span className="text-[10px] text-slate-400">{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                        </div>
                                        <div className="p-3">
                                            <p className="font-medium text-slate-700 text-xs mb-1 line-clamp-1">{msg.metadata.topic}</p>
                                            <p className="text-[10px] text-slate-500">{msg.metadata.unitCount} knowledge units ready for review.</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    }

                    if (msg.type === 'progress' && msg.metadata?.jobStatus) {
                        return (
                            <div key={msg.id} className="flex items-start gap-2">
                                <ViviAvatar className="w-6 h-6 flex-shrink-0 mt-0.5" />
                                <div>
                                    <span className="text-[10px] font-medium text-indigo-500 mb-1 block">Vivi</span>
                                    {renderProgressCard(msg.metadata.jobStatus)}
                                    <span className="text-[10px] text-slate-400 mt-1 block">
                                        {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                </div>
                            </div>
                        );
                    }

                    if (msg.type === 'edit-status') {
                        return <React.Fragment key={msg.id}>{renderEditStatusCard(msg)}</React.Fragment>;
                    }

                    // User messages
                    if (msg.role === 'user') {
                        return (
                            <div key={msg.id} className="flex flex-col items-end">
                                <div className="max-w-[85%] rounded-2xl px-3 py-2 text-sm shadow-sm bg-[var(--accent-primary)] text-white rounded-br-none">
                                    {msg.content}
                                </div>
                                <span className="text-[10px] text-slate-400 mt-1 px-1">
                                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>
                        );
                    }

                    // Assistant text messages — with avatar + markdown
                    return (
                        <div key={msg.id} className="flex items-start gap-2">
                            <ViviAvatar className="w-6 h-6 flex-shrink-0 mt-0.5" />
                            <div className="max-w-[85%]">
                                <span className="text-[10px] font-medium text-indigo-500 mb-1 block">Vivi</span>
                                <div className="rounded-2xl px-3 py-2 text-sm shadow-sm bg-white border border-slate-100 text-slate-700 rounded-tl-none">
                                    {msg.content ? (
                                        <div className="vivi-markdown prose prose-sm prose-slate max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
                                            <Markdown>{msg.content}</Markdown>
                                        </div>
                                    ) : (isStreaming ? (
                                        <span className="flex items-center gap-1.5 text-slate-400">
                                            <Loader2 className="w-3 h-3 animate-spin" />
                                            Thinking...
                                        </span>
                                    ) : null)}
                                </div>
                                <span className="text-[10px] text-slate-400 mt-1 px-1 block">
                                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>
                        </div>
                    );
                })}

                {isGeneratingSpec && (
                    <div className="flex items-start gap-2 animate-pulse">
                        <ViviAvatar className="w-6 h-6 flex-shrink-0 mt-0.5" />
                        <div className="rounded-2xl px-3 py-2 text-sm shadow-sm bg-white border border-slate-100 text-slate-700 rounded-tl-none flex items-center gap-2">
                            <Loader2 className="w-3 h-3 animate-spin text-[var(--accent-primary)]" />
                            <span>Generating specification...</span>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="flex-shrink-0 p-3 bg-white/40 border-t border-[var(--border-color)]">
                <div className="relative group">
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask AI to modify..."
                        className="w-full resize-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 pr-10 text-sm focus:border-[var(--accent-primary)] focus:ring-2 focus:ring-[var(--accent-primary)]/10 outline-none transition-all shadow-sm group-hover:shadow-md h-[42px] overflow-hidden leading-snug placeholder:text-slate-400"
                        rows={1}
                        style={{ minHeight: '42px' }}
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || isAnyJobRunning}
                        className="absolute right-1.5 top-1/2 -translate-y-1/2 p-1.5 rounded-lg bg-[var(--accent-primary)] text-white shadow-sm hover:shadow-md hover:bg-[var(--accent-secondary)] disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95"
                    >
                        {isAnyJobRunning ? <Loader2 className="w-3 h-3 animate-spin" /> : <Send className="w-3 h-3" />}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default RightChatPanel;
