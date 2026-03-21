import React, { useState, useEffect } from 'react';
import { Loader2, Sparkles, AlignLeft, MessageSquare, MousePointerClick, Palette } from 'lucide-react';
import { getStyleOptions, getStyle, saveStyle } from '../api/services';

interface StyleViewProps {
  specId: string;
  onStyleSaved: () => void;
}

const COLOR_MAP: Record<string, string> = {
  indigo: '#4f46e5',
  emerald: '#059669',
  rose: '#e11d48',
  amber: '#d97706',
  slate: '#475569',
};

const StyleView: React.FC<StyleViewProps> = ({ specId, onStyleSaved }) => {
  const [options, setOptions] = useState<Record<string, any>>({});
  const [values, setValues] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [optRes, saved] = await Promise.all([
          getStyleOptions(),
          getStyle(specId),
        ]);
        setOptions(optRes.options);
        const defaults: Record<string, any> = {};
        for (const [key, opt] of Object.entries(optRes.options)) {
          defaults[key] = (opt as any).default;
        }
        setValues({ ...defaults, ...saved });
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [specId]);

  const handleChange = (key: string, value: any) => {
    setValues(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await saveStyle(specId, values);
      onStyleSaved();
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-indigo-500" />
      </div>
    );
  }

  const renderSlider = (key: string, opt: any) => {
    const val = values[key];
    const allLabels = opt.labels || {};
    const allDescs = opt.descs || {};
    return (
      <div className="space-y-4 mt-2">
        <input
          type="range"
          min={opt.min}
          max={opt.max}
          value={val}
          onChange={e => handleChange(key, parseInt(e.target.value))}
          className="w-full h-2 bg-slate-200 rounded-full appearance-none cursor-pointer accent-indigo-500 focus:outline-none focus:ring-4 focus:ring-indigo-500/20 transition-all"
        />
        <div className="flex justify-between relative px-1">
          {Array.from({ length: opt.max - opt.min + 1 }, (_, i) => i + opt.min).map(n => (
            <span
              key={n}
              className={`text-[10px] cursor-pointer transition-colors duration-200 ${n === val ? 'text-indigo-700 font-semibold' : 'text-slate-400 hover:text-indigo-500'
                }`}
              onClick={() => handleChange(key, n)}
            >
              {allLabels[n] || n}
            </span>
          ))}
        </div>
        {allDescs[val] && (
          <div key={val} className="mt-3 px-3 py-2.5 bg-indigo-50/70 border border-indigo-100/60 rounded-xl animate-in fade-in slide-in-from-bottom-1 duration-300 shadow-sm">
            <p className="text-[12px] text-indigo-700/80 leading-relaxed font-medium">{allDescs[val]}</p>
          </div>
        )}
      </div>
    );
  };

  const renderRadio = (key: string, opt: any) => {
    const val = values[key];
    return (
      <div className="grid gap-2 mt-1">
        {opt.choices.map((c: any) => {
          const isSelected = val === c.value;
          return (
            <button
              key={c.value}
              onClick={() => handleChange(key, c.value)}
              className={`relative text-left px-4 py-2.5 rounded-xl border-2 transition-all duration-300 group overflow-hidden ${isSelected
                  ? 'border-indigo-500 bg-indigo-50/60 shadow-md ring-4 ring-indigo-500/10 -translate-y-0.5'
                  : 'border-slate-100 bg-white/60 hover:border-indigo-200 hover:bg-white hover:shadow-md hover:-translate-y-0.5'
                }`}
            >
              <div className="flex items-center justify-between relative z-10">
                <div className={`text-sm font-bold ${isSelected ? 'text-indigo-700' : 'text-slate-700 group-hover:text-indigo-600'}`}>
                  {c.label}
                </div>
                {isSelected && (
                  <div className="flex items-center justify-center w-5 h-5 rounded-full bg-indigo-500 text-white shadow-sm">
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3.5} strokeLinecap="round" strokeLinejoin="round"><path d="M5 13l4 4L19 7" /></svg>
                  </div>
                )}
              </div>
              {c.desc && (
                <div className={`text-xs mt-1.5 relative z-10 leading-relaxed ${isSelected ? 'text-indigo-600/80 font-medium' : 'text-slate-500'}`}>
                  {c.desc}
                </div>
              )}
              {isSelected && (
                <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-bl from-indigo-200/50 to-transparent rounded-full translate-x-12 -translate-y-12" />
              )}
            </button>
          );
        })}
      </div>
    );
  };

  const renderColor = (key: string, opt: any) => {
    const val = values[key];
    return (
      <div className="grid grid-cols-3 gap-y-5 gap-x-2 pt-3 mt-1">
        {opt.choices.map((c: any) => {
          const isAuto = c.value === 'auto';
          const isSelected = val === c.value;
          return (
            <button
              key={c.value}
              onClick={() => handleChange(key, c.value)}
              className="flex flex-col items-center gap-2.5 group relative"
            >
              <div
                className={`w-12 h-12 rounded-full transition-all duration-300 ease-out flex items-center justify-center relative ${isSelected ? 'ring-4 ring-offset-2 ring-indigo-400 scale-110 shadow-lg shadow-indigo-500/30' : 'ring-1 ring-slate-200 shadow-sm group-hover:scale-110 group-hover:shadow-md'
                  }`}
                style={
                  isAuto
                    ? { background: 'conic-gradient(from 180deg at 50% 50%, #4f46e5, #0ea5e9, #10b981, #f59e0b, #e11d48, #c026d3, #4f46e5)' }
                    : { backgroundColor: c.hex || COLOR_MAP[c.value] || '#666' }
                }
              >
                {isAuto && !isSelected && <span className="text-white text-sm font-bold drop-shadow">✦</span>}
                {isSelected && (
                  <svg className="w-5 h-5 text-white drop-shadow-md animate-in zoom-in duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3} strokeLinecap="round" strokeLinejoin="round"><path d="M5 13l4 4L19 7" /></svg>
                )}
              </div>
              <span className={`text-xs transition-colors duration-200 ${isSelected ? 'text-indigo-600 font-bold' : 'text-slate-500 group-hover:text-indigo-600 font-medium'}`}>
                {c.label}
              </span>
            </button>
          );
        })}
      </div>
    );
  };

  const renderOption = (key: string, opt: any) => {
    let Icon = Sparkles;
    const lower = key.toLowerCase();
    if (lower.includes('dens')) Icon = AlignLeft;
    else if (lower.includes('tone') || lower.includes('writ')) Icon = MessageSquare;
    else if (lower.includes('interact')) Icon = MousePointerClick;
    else if (lower.includes('color')) Icon = Palette;

    return (
      <div
        key={key}
        className="bg-white/70 backdrop-blur-xl rounded-2xl border border-white/80 p-5 shadow-[0_4px_24px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_32px_rgba(79,70,229,0.06)] hover:-translate-y-0.5 transition-all duration-300"
      >
        <div className="flex items-center gap-2 mb-3">
          <div className="p-1.5 bg-indigo-100/50 rounded-lg text-indigo-500 shadow-sm border border-indigo-50">
            <Icon className="w-4 h-4" />
          </div>
          <h3 className="text-sm font-bold text-slate-800 tracking-wide">{opt.label}</h3>
        </div>
        {opt.type === 'slider' && renderSlider(key, opt)}
        {opt.type === 'radio' && renderRadio(key, opt)}
        {opt.type === 'color' && renderColor(key, opt)}
      </div>
    );
  };

  return (
    <div className="flex-1 flex flex-col relative overflow-hidden bg-transparent">
      <div className="flex-1 overflow-y-auto pb-28 scrollbar-thin scrollbar-thumb-slate-200">
        <div className="max-w-2xl mx-auto py-8 px-6">
          <h2 className="text-lg font-semibold text-slate-700 text-center mb-5 tracking-tight">
            Customize Your Own Style
          </h2>

          <div className="grid grid-cols-2 gap-4">
            {Object.entries(options).map(([key, opt]) => renderOption(key, opt))}
          </div>
        </div>
      </div>

      {/* Sticky Bottom Bar */}
      <div className="absolute bottom-0 inset-x-0 pb-10 pt-4 z-20 pointer-events-none bg-gradient-to-t from-white/50 to-transparent">
        <div className="max-w-2xl mx-auto px-6 pointer-events-auto">
          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full py-3.5 bg-gradient-to-r from-indigo-500 to-indigo-600 text-white rounded-xl font-bold text-sm tracking-wide hover:from-indigo-600 hover:to-indigo-700 transition-all duration-300 disabled:opacity-50 flex items-center justify-center gap-2 shadow-xl shadow-indigo-500/20 hover:shadow-indigo-500/40 active:scale-[0.98]"
          >
            {saving ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
            Save & Generate Document
          </button>
        </div>
      </div>
    </div>
  );
};

export default StyleView;
