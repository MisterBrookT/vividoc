import React, { useState, useEffect } from 'react';
import { Loader2, Sparkles } from 'lucide-react';
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
      <div className="space-y-3">
        <input
          type="range"
          min={opt.min}
          max={opt.max}
          value={val}
          onChange={e => handleChange(key, parseInt(e.target.value))}
          className="w-full h-2 bg-slate-200 rounded-full appearance-none cursor-pointer accent-indigo-500"
        />
        <div className="flex justify-between">
          {Array.from({ length: opt.max - opt.min + 1 }, (_, i) => i + opt.min).map(n => (
            <span
              key={n}
              className={`text-[10px] cursor-pointer transition-colors ${
                n === val ? 'text-indigo-600 font-semibold' : 'text-slate-400'
              }`}
              onClick={() => handleChange(key, n)}
            >
              {allLabels[n] || n}
            </span>
          ))}
        </div>
        {allDescs[val] && (
          <div className="mt-2 px-3 py-2 bg-indigo-50/60 rounded-lg transition-all">
            <p className="text-xs text-indigo-600/80 leading-relaxed">{allDescs[val]}</p>
          </div>
        )}
      </div>
    );
  };

  const renderRadio = (key: string, opt: any) => {
    const val = values[key];
    return (
      <div className="grid gap-2">
        {opt.choices.map((c: any) => (
          <button
            key={c.value}
            onClick={() => handleChange(key, c.value)}
            className={`text-left px-4 py-2.5 rounded-xl border-2 transition-all ${
              val === c.value
                ? 'border-indigo-400 bg-indigo-50/80 shadow-sm'
                : 'border-slate-100 bg-white hover:border-slate-200 hover:bg-slate-50'
            }`}
          >
            <div className={`text-sm font-medium ${val === c.value ? 'text-indigo-700' : 'text-slate-700'}`}>
              {c.label}
            </div>
            {c.desc && (
              <div className={`text-[11px] mt-0.5 ${val === c.value ? 'text-indigo-500' : 'text-slate-400'}`}>
                {c.desc}
              </div>
            )}
          </button>
        ))}
      </div>
    );
  };

  const renderColor = (key: string, opt: any) => {
    const val = values[key];
    return (
      <div className="grid grid-cols-3 gap-3 pt-1">
        {opt.choices.map((c: any) => {
          const isAuto = c.value === 'auto';
          return (
            <button
              key={c.value}
              onClick={() => handleChange(key, c.value)}
              className="flex flex-col items-center gap-1.5 group"
            >
              <div
                className={`w-12 h-12 rounded-full transition-all flex items-center justify-center ${
                  val === c.value ? 'ring-2 ring-offset-2 ring-slate-400 scale-110' : 'group-hover:scale-105'
                }`}
                style={
                  isAuto
                    ? { background: 'conic-gradient(#4f46e5, #059669, #d97706, #e11d48, #4f46e5)' }
                    : { backgroundColor: c.hex || COLOR_MAP[c.value] || '#666' }
                }
              >
                {isAuto && <span className="text-white text-xs font-bold drop-shadow">✦</span>}
              </div>
              <span className={`text-[11px] ${val === c.value ? 'text-indigo-600 font-semibold' : 'text-slate-400'}`}>
                {c.label}
              </span>
            </button>
          );
        })}
      </div>
    );
  };

  const renderOption = (key: string, opt: any) => {
    return (
      <div
        key={key}
        className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm hover:shadow-md transition-shadow"
      >
        <h3 className="text-sm font-semibold text-slate-800 mb-3">{opt.label}</h3>
        {opt.type === 'slider' && renderSlider(key, opt)}
        {opt.type === 'radio' && renderRadio(key, opt)}
        {opt.type === 'color' && renderColor(key, opt)}
      </div>
    );
  };

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-2xl mx-auto py-10 px-6">
        <h2 className="text-lg font-semibold text-slate-700 text-center mb-6">
          Customize your own style
        </h2>

        <div className="grid grid-cols-2 gap-4">
          {Object.entries(options).map(([key, opt]) => renderOption(key, opt))}
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="mt-8 w-full py-3 bg-indigo-600 text-white rounded-xl font-medium text-sm hover:bg-indigo-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg hover:shadow-indigo-500/25 active:scale-[0.98]"
        >
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
          Save & Generate Document
        </button>
      </div>
    </div>
  );
};

export default StyleView;
