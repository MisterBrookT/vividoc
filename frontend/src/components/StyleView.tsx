import React, { useState, useEffect } from 'react';
import { Loader2, Play, Type, MousePointerClick, Sparkles } from 'lucide-react';
import { generateStyleOptions, getStyle, saveStyle } from '../api/services';

interface StyleOption {
  id: string;
  label: string;
  description: string;
}

interface StyleDimension {
  id: string;
  label: string;
  options: StyleOption[];
}

interface StyleViewProps {
  specId: string;
  onStyleSaved: () => void;
}

type SelectionValue = { type: 'auto' } | { type: 'option'; description: string } | { type: 'custom'; text: string };

const StyleView: React.FC<StyleViewProps> = ({ specId, onStyleSaved }) => {
  const [textDimensions, setTextDimensions] = useState<StyleDimension[]>([]);
  const [interactionDimensions, setInteractionDimensions] = useState<StyleDimension[]>([]);
  const [textSelections, setTextSelections] = useState<Record<string, SelectionValue>>({});
  const [interactionSelections, setInteractionSelections] = useState<Record<string, SelectionValue>>({});
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadOptions();
  }, [specId]);

  const loadOptions = async () => {
    setLoading(true);
    setError(null);
    try {
      // Load saved style first
      const saved = await getStyle(specId);

      // Check if we have cached options in saved style
      if (saved._options) {
        setTextDimensions(saved._options.text_dimensions || []);
        setInteractionDimensions(saved._options.interaction_dimensions || []);
        restoreSelections(saved, saved._options.text_dimensions || [], saved._options.interaction_dimensions || []);
      } else {
        // Generate new options from LLM
        await generateOptions(saved);
      }
    } catch {
      setError('Failed to load style options');
    } finally {
      setLoading(false);
    }
  };

  const generateOptions = async (savedStyle?: Record<string, any>) => {
    setGenerating(true);
    try {
      const res = await generateStyleOptions(specId);
      const opts = res.options;
      const textDims = opts.text_dimensions || [];
      const intDims = opts.interaction_dimensions || [];
      setTextDimensions(textDims);
      setInteractionDimensions(intDims);

      // Initialize all to auto
      const tSel: Record<string, SelectionValue> = {};
      textDims.forEach((d: StyleDimension) => { tSel[d.id] = { type: 'auto' }; });
      const iSel: Record<string, SelectionValue> = {};
      intDims.forEach((d: StyleDimension) => { iSel[d.id] = { type: 'auto' }; });

      if (savedStyle) {
        restoreSelections(savedStyle, textDims, intDims);
      } else {
        setTextSelections(tSel);
        setInteractionSelections(iSel);
      }

      // Cache options in style.json so we don't re-generate
      const currentSaved = savedStyle || {};
      await saveStyle(specId, { ...currentSaved, _options: opts });
    } catch {
      setError('Failed to generate style options');
    } finally {
      setGenerating(false);
    }
  };

  const restoreSelections = (
    saved: Record<string, any>,
    textDims: StyleDimension[],
    intDims: StyleDimension[]
  ) => {
    const tSel: Record<string, SelectionValue> = {};
    textDims.forEach(d => { tSel[d.id] = { type: 'auto' }; });
    const savedText = saved.text_selections || {};
    for (const [key, val] of Object.entries(savedText)) {
      if (val && typeof val === 'string' && val.startsWith('__custom__:')) {
        tSel[key] = { type: 'custom', text: val.slice('__custom__:'.length) };
      } else if (val && typeof val === 'string') {
        tSel[key] = { type: 'option', description: val };
      } else {
        tSel[key] = { type: 'auto' };
      }
    }
    setTextSelections(tSel);

    const iSel: Record<string, SelectionValue> = {};
    intDims.forEach(d => { iSel[d.id] = { type: 'auto' }; });
    const savedInt = saved.interaction_selections || {};
    for (const [key, val] of Object.entries(savedInt)) {
      if (val && typeof val === 'string' && val.startsWith('__custom__:')) {
        iSel[key] = { type: 'custom', text: val.slice('__custom__:'.length) };
      } else if (val && typeof val === 'string') {
        iSel[key] = { type: 'option', description: val };
      } else {
        iSel[key] = { type: 'auto' };
      }
    }
    setInteractionSelections(iSel);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Convert selections to description strings for backend
      const textSel: Record<string, string> = {};
      for (const [key, val] of Object.entries(textSelections)) {
        if (val.type === 'option') textSel[key] = val.description;
        else if (val.type === 'custom' && val.text.trim()) textSel[key] = '__custom__:' + val.text.trim();
        else textSel[key] = '';
      }
      const intSel: Record<string, string> = {};
      for (const [key, val] of Object.entries(interactionSelections)) {
        if (val.type === 'option') intSel[key] = val.description;
        else if (val.type === 'custom' && val.text.trim()) intSel[key] = '__custom__:' + val.text.trim();
        else intSel[key] = '';
      }

      await saveStyle(specId, {
        text_selections: textSel,
        interaction_selections: intSel,
        _options: { text_dimensions: textDimensions, interaction_dimensions: interactionDimensions },
      });
      onStyleSaved();
    } finally {
      setSaving(false);
    }
  };

  const renderDimension = (
    dim: StyleDimension,
    selections: Record<string, SelectionValue>,
    setSelections: React.Dispatch<React.SetStateAction<Record<string, SelectionValue>>>
  ) => {
    const sel = selections[dim.id] || { type: 'auto' };

    return (
      <div key={dim.id} className="bg-white/70 backdrop-blur-xl rounded-2xl border border-white/80 p-5 shadow-[0_4px_24px_rgba(0,0,0,0.02)]">
        <h4 className="text-sm font-bold text-slate-700 mb-3">{dim.label}</h4>
        <div className="space-y-2">
          {/* Auto option */}
          <button
            onClick={() => setSelections(prev => ({ ...prev, [dim.id]: { type: 'auto' } }))}
            className={`w-full text-left px-4 py-2.5 rounded-xl border-2 transition-all ${
              sel.type === 'auto'
                ? 'border-indigo-500 bg-indigo-50/60 shadow-md ring-4 ring-indigo-500/10'
                : 'border-slate-100 bg-white/60 hover:border-indigo-200 hover:bg-white hover:shadow-md'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className={`text-sm font-bold ${sel.type === 'auto' ? 'text-indigo-700' : 'text-slate-600'}`}>
                Auto
              </div>
              {sel.type === 'auto' && (
                <div className="flex items-center justify-center w-5 h-5 rounded-full bg-indigo-500 text-white shadow-sm">
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3.5}><path d="M5 13l4 4L19 7" /></svg>
                </div>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-0.5">Let the AI decide</p>
          </button>

          {/* LLM-generated options */}
          {dim.options.map(opt => {
            const isSelected = sel.type === 'option' && sel.description === opt.description;
            return (
              <button
                key={opt.id}
                onClick={() => setSelections(prev => ({ ...prev, [dim.id]: { type: 'option', description: opt.description } }))}
                className={`w-full text-left px-4 py-2.5 rounded-xl border-2 transition-all ${
                  isSelected
                    ? 'border-indigo-500 bg-indigo-50/60 shadow-md ring-4 ring-indigo-500/10'
                    : 'border-slate-100 bg-white/60 hover:border-indigo-200 hover:bg-white hover:shadow-md'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className={`text-sm font-bold ${isSelected ? 'text-indigo-700' : 'text-slate-700'}`}>
                    {opt.label}
                  </div>
                  {isSelected && (
                    <div className="flex items-center justify-center w-5 h-5 rounded-full bg-indigo-500 text-white shadow-sm">
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3.5}><path d="M5 13l4 4L19 7" /></svg>
                    </div>
                  )}
                </div>
                <p className={`text-xs mt-1 leading-relaxed ${isSelected ? 'text-indigo-600/80' : 'text-slate-500'}`}>
                  {opt.description}
                </p>
              </button>
            );
          })}

          {/* Custom option */}
          <button
            onClick={() => setSelections(prev => ({ ...prev, [dim.id]: { type: 'custom', text: sel.type === 'custom' ? sel.text : '' } }))}
            className={`w-full text-left px-4 py-2.5 rounded-xl border-2 transition-all ${
              sel.type === 'custom'
                ? 'border-indigo-500 bg-indigo-50/60 shadow-md ring-4 ring-indigo-500/10'
                : 'border-slate-100 bg-white/60 hover:border-indigo-200 hover:bg-white hover:shadow-md'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className={`text-sm font-bold ${sel.type === 'custom' ? 'text-indigo-700' : 'text-slate-600'}`}>
                Custom
              </div>
              {sel.type === 'custom' && (
                <div className="flex items-center justify-center w-5 h-5 rounded-full bg-indigo-500 text-white shadow-sm">
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3.5}><path d="M5 13l4 4L19 7" /></svg>
                </div>
              )}
            </div>
          </button>
          {sel.type === 'custom' && (
            <textarea
              value={sel.text}
              onChange={e => setSelections(prev => ({ ...prev, [dim.id]: { type: 'custom', text: e.target.value } }))}
              placeholder="Describe your preferred style..."
              rows={2}
              className="w-full text-sm bg-white border border-slate-200 rounded-xl px-4 py-2.5 outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/10 transition-all resize-none"
            />
          )}
        </div>
      </div>
    );
  };

  if (loading || generating) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center gap-4">
        <div className="relative">
          <div className="w-16 h-16 rounded-2xl bg-indigo-50 flex items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
          </div>
        </div>
        <div className="text-center">
          <p className="text-base font-semibold text-slate-700">
            {generating ? 'Generating Style Options' : 'Loading...'}
          </p>
          <p className="text-sm text-slate-400 mt-1">
            {generating ? 'Analyzing your content to suggest the best styles...' : 'Please wait...'}
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center gap-3">
        <p className="text-sm text-red-500">{error}</p>
        <button onClick={() => generateOptions()} className="text-sm text-indigo-500 hover:underline">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-200">
        <div className="max-w-6xl mx-auto py-8 px-6">
          <h2 className="text-lg font-semibold text-slate-700 text-center mb-2 tracking-tight">
            Customize Your Style
          </h2>
          <p className="text-xs text-slate-400 text-center mb-6">Options generated based on your document content</p>

          <div className="grid grid-cols-2 gap-20">
            {/* Text Style Column */}
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="p-1.5 bg-indigo-100/50 rounded-lg text-indigo-500">
                  <Type className="w-4 h-4" />
                </div>
                <h3 className="text-sm font-bold text-slate-700">Writing Style</h3>
              </div>
              <div className="space-y-4">
                {textDimensions.map(dim => renderDimension(dim, textSelections, setTextSelections))}
              </div>
            </div>

            {/* Interaction Style Column */}
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="p-1.5 bg-indigo-100/50 rounded-lg text-indigo-500">
                  <MousePointerClick className="w-4 h-4" />
                </div>
                <h3 className="text-sm font-bold text-slate-700">Interaction Style</h3>
              </div>
              <div className="space-y-4">
                {interactionDimensions.map(dim => renderDimension(dim, interactionSelections, setInteractionSelections))}
              </div>
            </div>
          </div>

          {/* Regenerate button */}
          <div className="flex justify-center mt-6">
            <button
              onClick={() => generateOptions()}
              disabled={generating}
              className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-indigo-500 transition-colors"
            >
              <Sparkles className="w-3.5 h-3.5" />
              Regenerate options
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="flex-shrink-0 p-4 border-t border-[var(--border-color)] bg-white/30 backdrop-blur-sm">
        <div className="px-6">
          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full btn-primary py-3 px-4 rounded-xl font-semibold flex items-center justify-center gap-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed group"
          >
            {saving ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                <span>Next: Generate Document</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default StyleView;
