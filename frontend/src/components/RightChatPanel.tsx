
import React, { useState, useEffect, useRef } from 'react';
import { Send, Sparkles, AlertCircle, CheckCircle2, Loader2, FileText, ArrowRight } from 'lucide-react';
import type { JobStatus, DocumentSpec } from '../types/models';

interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: number;
    type?: 'text' | 'spec-notification';
    metadata?: any;
}

interface RightChatPanelProps {
    jobStatus: JobStatus | null;
    onSendMessage: (message: string) => void;
    isGeneratingSpec: boolean;
    spec: DocumentSpec | null;
    onViewSpec: () => void;
}

const RightChatPanel: React.FC<RightChatPanelProps> = ({
    jobStatus,
    onSendMessage,
    isGeneratingSpec,
    spec,
    onViewSpec,
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
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const lastSpecIdRef = useRef<string | null>(null);

    // Sync spec notification
    useEffect(() => {
        if (spec && spec.id !== lastSpecIdRef.current) {
            // New spec generated
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
            lastSpecIdRef.current = spec.id;
        } else if (!spec) {
            lastSpecIdRef.current = null;
        }
    }, [spec]);

    // Scroll to bottom when messages change
    // 注意：不能用默认的 scrollIntoView，它会连带滚动所有祖先容器，
    // 导致整个页面布局上移。用 block:'nearest' 限制只滚动最近的可滚动容器。
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, [messages, jobStatus, isGeneratingSpec]);

    const handleSend = () => {
        if (!input.trim()) return;

        const newMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: Date.now(),
        };

        setMessages((prev) => [...prev, newMessage]);
        onSendMessage(input);
        setInput('');
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Render Status Card
    const renderStatusCard = () => {
        if (!jobStatus) return null;
        const isRunning = jobStatus.status === 'running';
        if (!isRunning && jobStatus.status !== 'failed' && jobStatus.status !== 'completed') return null;

        const { phase, ku_progress, overall_percent } = jobStatus.progress;

        return (
            <div className="mx-2 my-2 p-3 bg-white/80 backdrop-blur-sm rounded-xl border border-indigo-100 shadow-sm animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div className="flex items-center gap-2 mb-2">
                    {isRunning ? (
                        <div className="relative flex h-2.5 w-2.5">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-indigo-500"></span>
                        </div>
                    ) : jobStatus.status === 'failed' ? (
                        <AlertCircle className="w-3.5 h-3.5 text-red-500" />
                    ) : (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                    )}
                    <span className="text-xs font-semibold text-slate-700">
                        {isRunning ? 'Generating Document...' :
                            jobStatus.status === 'failed' ? 'Generation Failed' : 'Completed'}
                    </span>
                </div>

                {/* Phase Indicator */}
                <div className="space-y-2">
                    <div className="flex justify-between text-[10px] text-slate-500 mb-0.5">
                        <span>Progress</span>
                        <span>{Math.round((overall_percent || 0) * 100)}%</span>
                    </div>
                    <div className="h-1 w-full bg-slate-100 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-indigo-500 rounded-full transition-all duration-500 ease-out"
                            style={{ width: `${(overall_percent || 0) * 100}%` }}
                        />
                    </div>

                    <div className="mt-2 space-y-1.5">
                        <div className={`flex items-center gap-1.5 text-[10px] ${phase === 'planning' ? 'text-indigo-600 font-medium' : 'text-slate-400'}`}>
                            <div className={`w-1 h-1 rounded-full ${phase === 'planning' ? 'bg-indigo-500 animate-pulse' : 'bg-slate-300'}`} />
                            Planning Structure
                        </div>

                        <div className={`flex items-center gap-1.5 text-[10px] ${phase === 'executing' ? 'text-indigo-600 font-medium' : 'text-slate-400'}`}>
                            <div className={`w-1 h-1 rounded-full ${phase === 'executing' ? 'bg-indigo-500 animate-pulse' : 'bg-slate-300'}`} />
                            Generating Content
                        </div>

                        {/* Active KUs */}
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

    const isAnyJobRunning = jobStatus?.status === 'running' || isGeneratingSpec;

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
                            <div key={msg.id} className="flex flex-col items-start animate-in fade-in zoom-in-95 duration-300">
                                <div className="max-w-[95%] bg-white border border-slate-200 rounded-xl shadow-sm text-sm overflow-hidden hover:shadow-md transition-shadow cursor-pointer group" onClick={onViewSpec}>
                                    <div className="px-3 py-2 bg-[var(--surface-color)]/50 border-b border-slate-100 flex items-center justify-between">
                                        <div className="flex items-center gap-1.5 text-xs font-semibold text-indigo-600">
                                            <FileText className="w-3.5 h-3.5" />
                                            <span>Spec Generated</span>
                                        </div>
                                        <span className="text-[10px] text-slate-400">{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                    </div>
                                    <div className="p-3">
                                        <p className="font-medium text-slate-700 text-xs mb-1 line-clamp-1">{msg.metadata.topic}</p>
                                        <p className="text-[10px] text-slate-500 mb-2">{msg.metadata.unitCount} knowledge units ready for review.</p>
                                        <button className="w-full text-xs flex items-center justify-center gap-1 text-indigo-600 bg-indigo-50 py-1.5 rounded-lg font-medium group-hover:bg-indigo-100 transition-colors">
                                            View Specification
                                            <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )
                    }

                    return (
                        <div
                            key={msg.id}
                            className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                        >
                            <div
                                className={`max-w-[95%] rounded-2xl px-3 py-2 text-sm shadow-sm whitespace-pre-wrap ${msg.role === 'user'
                                    ? 'bg-[var(--accent-primary)] text-white rounded-br-none'
                                    : 'bg-white border border-slate-100 text-slate-700 rounded-bl-none'
                                    }`}
                            >
                                {msg.content}
                            </div>
                            <span className="text-[10px] text-slate-400 mt-1 px-1">
                                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </div>
                    );
                })}

                {/* Helper message for Spec Generation */}
                {isGeneratingSpec && (
                    <div className="flex flex-col items-start animate-pulse">
                        <div className="max-w-[90%] rounded-2xl px-3 py-2 text-sm shadow-sm bg-white border border-slate-100 text-slate-700 rounded-bl-none flex items-center gap-2">
                            <Loader2 className="w-3 h-3 animate-spin text-[var(--accent-primary)]" />
                            <span>Generating specification...</span>
                        </div>
                    </div>
                )}

                {/* Status Card Injection */}
                {renderStatusCard()}

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
