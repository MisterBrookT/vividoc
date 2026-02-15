import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Sparkles, AlertCircle, CheckCircle2, Loader2, FileText } from 'lucide-react';
import type { JobStatus, DocumentSpec } from '../types/models';
import { streamChat } from '../api/services';

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
}

const RightChatPanel: React.FC<RightChatPanelProps> = ({
    jobStatus,
    onSendMessage,
    isGeneratingSpec,
    spec,
    specJustGenerated,
    onSpecJustGeneratedConsumed,
    onHtmlUpdated,
}) => {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: 'welcome',
            role: 'assistant',
            content: "Hi! I'm Vivi, your AI assistant. I can help you refine the specification or modify the generated document. What would you like to do?",
            timestamp: Date.now(),
        },
    ]);
    const [input, setInput] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const progressMsgIdRef = useRef<string | null>(null);

    // Only show spec notification when spec was freshly generated
    useEffect(() => {
        if (specJustGenerated && spec) {
            const newMessage: Message = {
                id: `spec-${spec.id}`,
                role: 'assistant',
                content: 'Specification generated!',
                timestamp: Date.now(),
                type: 'spec-notification',
                metadata: {
                    specId: spec.id,
                    topic: spec.topic,
                    unitCount: spec.knowledge_units.length
                }
            };
            setMessages((prev) => [...prev, newMessage]);
            onSpecJustGeneratedConsumed();
        }
    }, [specJustGenerated, spec, onSpecJustGeneratedConsumed]);

    // Insert/update progress as a timestamped message in the list
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
                id: msgId,
                role: 'assistant',
                content: '',
                timestamp: Date.now(),
                type: 'progress',
                metadata: { jobStatus },
            }]);
        } else if (progressMsgIdRef.current) {
            setMessages((prev) => prev.map(m =>
                m.id === progressMsgIdRef.current
                    ? { ...m, metadata: { jobStatus } }
                    : m
            ));
        }

        if (isCompleted || isFailed) {
            progressMsgIdRef.current = null;
        }
    }, [jobStatus]);

    // Scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, [messages, isStreaming]);

    const handleSend = useCallback(async () => {
        if (!input.trim() || isStreaming) return;
        const userMsg = input.trim();
        setInput('');

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: userMsg,
            timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, userMessage]);
        onSendMessage(userMsg);

        if (spec?.id) {
            const assistantMsgId = `assistant-${Date.now()}`;
            // Start as a normal text message; may switch to edit-status card
            const assistantMessage: Message = {
                id: assistantMsgId,
                role: 'assistant',
                content: '',
                timestamp: Date.now(),
                type: 'text',
                metadata: { editMode: false, editDone: false, description: '' },
            };
            setMessages((prev) => [...prev, assistantMessage]);
            setIsStreaming(true);

            let isEditMode = false;
            let rawContent = '';

            try {
                await streamChat(spec.id, userMsg, (event) => {
                    if (event.type === 'edit_mode_start') {
                        isEditMode = true;
                        // Switch message type to edit-status card
                        setMessages((prev) => prev.map(m =>
                            m.id === assistantMsgId
                                ? { ...m, type: 'edit-status', metadata: { editMode: true, editDone: false, description: '' } }
                                : m
                        ));
                    } else if (event.type === 'token' && event.content) {
                        rawContent += event.content;
                        if (isEditMode) {
                            // Extract the description text (between [EDIT_MODE] and first ```edit block)
                            const cleaned = rawContent.replace('[EDIT_MODE]', '').trim();
                            const editBlockStart = cleaned.indexOf('```edit');
                            const desc = editBlockStart > 0
                                ? cleaned.substring(0, editBlockStart).trim()
                                : cleaned.replace(/```[\s\S]*$/, '').trim();
                            setMessages((prev) => prev.map(m =>
                                m.id === assistantMsgId
                                    ? { ...m, metadata: { ...m.metadata, description: desc } }
                                    : m
                            ));
                        } else {
                            // Normal text response
                            setMessages((prev) => prev.map(m =>
                                m.id === assistantMsgId
                                    ? { ...m, content: rawContent }
                                    : m
                            ));
                        }
                    } else if (event.type === 'html_updated' && event.html) {
                        // Mark edit as done
                        setMessages((prev) => prev.map(m =>
                            m.id === assistantMsgId
                                ? { ...m, metadata: { ...m.metadata, editDone: true } }
                                : m
                        ));
                        onHtmlUpdated?.(event.html);
                    } else if (event.type === 'error') {
                        setMessages((prev) => prev.map(m =>
                            m.id === assistantMsgId
                                ? {
                                    ...m,
                                    type: 'text',
                                    content: `⚠️ Error: ${event.content}`,
                                    metadata: { editMode: false, editDone: false }
                                  }
                                : m
                        ));
                    }
                });
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
    }, [input, isStreaming, spec, onSendMessage, onHtmlUpdated]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const renderEditStatusCard = (msg: Message) => {
        const { editDone, description } = msg.metadata || {};
        return (
            <div className="flex flex-col items-start">
                <div className="max-w-[95%] bg-white border border-indigo-100 rounded-xl shadow-sm text-sm overflow-hidden">
                    <div className="px-3 py-2 border-b border-indigo-50 flex items-center justify-between">
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-indigo-600">
                            {editDone ? (
                                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                            ) : (
                                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            )}
                            <span>{editDone ? 'Document Updated' : 'Editing Document...'}</span>
                        </div>
                        <span className="text-[10px] text-slate-400">
                            {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
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
                        {isRunning ? 'Generating Document...' :
                            js.status === 'failed' ? 'Generation Failed' : 'Completed'}
                    </span>
                </div>
                <div className="space-y-2">
                    <div className="flex justify-between text-[10px] text-slate-500 mb-0.5">
                        <span>Progress</span>
                        <span>{cappedPercent}%</span>
                    </div>
                    <div className="h-1 w-full bg-slate-100 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-indigo-500 rounded-full transition-all duration-500 ease-out"
                            style={{ width: `${cappedPercent}%` }}
                        />
                    </div>
                    <div className="mt-2 space-y-1.5">
                        <div className={`flex items-center gap-1.5 text-[10px] ${phase === 'executing' ? 'text-indigo-600 font-medium' : 'text-slate-400'}`}>
                            <div className={`w-1 h-1 rounded-full ${phase === 'executing' ? 'bg-indigo-500 animate-pulse' : 'bg-slate-300'}`} />
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
                        <div className={`flex items-center gap-1.5 text-[10px] ${phase === 'evaluating' ? 'text-indigo-600 font-medium' : 'text-slate-400'}`}>
                            <div className={`w-1 h-1 rounded-full ${phase === 'evaluating' ? 'bg-indigo-500 animate-pulse' : 'bg-slate-300'}`} />
                            Refining & Finalizing
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const isAnyJobRunning = jobStatus?.status === 'running' || isGeneratingSpec || isStreaming;

    return (
        <div className="w-[300px] h-full bg-white/60 backdrop-blur-xl border-l border-[var(--border-color)] flex flex-col relative z-20 transition-all duration-300">
            {/* Header */}
            <div className="flex-shrink-0 h-16 px-4 border-b border-[var(--border-color)] flex items-center justify-between bg-white/40">
                <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-[var(--accent-primary)]" />
                    <h2 className="text-sm font-semibold text-slate-700">AI Assistant</h2>
                </div>
                <div className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]"></span>
                    <span className="text-[10px] font-medium text-slate-400">Ready</span>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent p-3 space-y-3">
                {messages.map((msg) => {
                    if (msg.type === 'spec-notification') {
                        return (
                            <div key={msg.id} className="flex flex-col items-start">
                                <div className="max-w-[95%] bg-white border border-slate-200 rounded-xl shadow-sm text-sm overflow-hidden hover:shadow-md transition-shadow cursor-pointer group">
                                    <div className="px-3 py-2 border-b border-slate-100 flex items-center justify-between">
                                        <div className="flex items-center gap-1.5 text-xs font-semibold text-indigo-600">
                                            <FileText className="w-3.5 h-3.5" />
                                            <span>Spec Generated</span>
                                        </div>
                                        <span className="text-[10px] text-slate-400">{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                    </div>
                                    <div className="p-3">
                                        <p className="font-medium text-slate-700 text-xs mb-1 line-clamp-1">{msg.metadata.topic}</p>
                                        <p className="text-[10px] text-slate-500 mb-2">{msg.metadata.unitCount} knowledge units ready for review.</p>
                                    </div>
                                </div>
                            </div>
                        );
                    }

                    if (msg.type === 'progress' && msg.metadata?.jobStatus) {
                        return (
                            <div key={msg.id} className="flex flex-col items-start">
                                <div className="max-w-[95%]">
                                    {renderProgressCard(msg.metadata.jobStatus)}
                                </div>
                                <span className="text-[10px] text-slate-400 mt-1 px-1">
                                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>
                        );
                    }

                    if (msg.type === 'edit-status') {
                        return (
                            <React.Fragment key={msg.id}>
                                {renderEditStatusCard(msg)}
                            </React.Fragment>
                        );
                    }

                    return (
                        <div
                            key={msg.id}
                            className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                        >
                            <div
                                className={`max-w-[95%] rounded-2xl px-3 py-2 text-sm shadow-sm whitespace-pre-wrap ${
                                    msg.role === 'user'
                                        ? 'bg-[var(--accent-primary)] text-white rounded-br-none'
                                        : 'bg-white border border-slate-100 text-slate-700 rounded-bl-none'
                                }`}
                            >
                                {msg.content || (isStreaming && msg.role === 'assistant' ? (
                                    <span className="flex items-center gap-1.5 text-slate-400">
                                        <Loader2 className="w-3 h-3 animate-spin" />
                                        Thinking...
                                    </span>
                                ) : null)}
                            </div>
                            <span className="text-[10px] text-slate-400 mt-1 px-1">
                                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </div>
                    );
                })}

                {isGeneratingSpec && (
                    <div className="flex flex-col items-start animate-pulse">
                        <div className="max-w-[90%] rounded-2xl px-3 py-2 text-sm shadow-sm bg-white border border-slate-100 text-slate-700 rounded-bl-none flex items-center gap-2">
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
                        {isAnyJobRunning ? (
                            <Loader2 className="w-3 h-3 animate-spin" />
                        ) : (
                            <Send className="w-3 h-3" />
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default RightChatPanel;
