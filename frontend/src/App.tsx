import { useState } from 'react';

const CASES = [
  {
    slug: 'fourier_transform',
    title: 'Fourier Transform',
    category: 'Temporal Control',
    desc: 'Signal decomposition, Gibbs phenomenon, and epicycles tracing waveforms in real time.',
  },
  {
    slug: 'lorenz_attractor',
    title: 'Lorenz Attractor',
    category: 'Parameter Exploration',
    desc: 'Deterministic chaos, butterfly effect, and phase transitions controlled by ρ.',
  },
  {
    slug: 'geometric_optics',
    title: 'Geometric Optics',
    category: 'Direct Manipulation',
    desc: 'Drag lenses and sources to trace real-time refraction paths.',
  },
  {
    slug: 'neural_network',
    title: 'Neural Network',
    category: 'Freeform Construction',
    desc: 'Build a network layer by layer and watch forward propagation unfold.',
  },
  {
    slug: 'quantum_orbitals',
    title: 'Quantum Orbitals',
    category: 'State Switching',
    desc: 'Switch between 1s, 2p, 3d electron probability clouds.',
  },
  {
    slug: 'voronoi',
    title: 'Voronoi Tessellation',
    category: 'Inspection',
    desc: 'Hover to reveal spatial partitioning and proximity relationships.',
  },
  {
    slug: 'mobius_strip',
    title: 'Möbius Strip',
    category: 'Spatial Navigation',
    desc: 'Rotate a non-orientable topological surface in three dimensions.',
  },
  {
    slug: 'entropy',
    title: 'Entropy',
    category: 'Scroll-driven Narrative',
    desc: 'Scroll through thermodynamic irreversibility as particles mix.',
  },
];

const CATEGORY_COLORS: Record<string, string> = {
  'Temporal Control':      'bg-pink-950 text-pink-300 border-pink-800',
  'Parameter Exploration': 'bg-cyan-950 text-cyan-300 border-cyan-800',
  'Direct Manipulation':   'bg-emerald-950 text-emerald-300 border-emerald-800',
  'Freeform Construction': 'bg-yellow-950 text-yellow-300 border-yellow-800',
  'State Switching':       'bg-blue-950 text-blue-300 border-blue-800',
  'Inspection':            'bg-purple-950 text-purple-300 border-purple-800',
  'Spatial Navigation':    'bg-sky-950 text-sky-300 border-sky-800',
  'Scroll-driven Narrative':'bg-red-950 text-red-300 border-red-800',
};

function CaseCard({ c, onOpen }: { c: typeof CASES[0]; onOpen: (slug: string) => void }) {
  return (
    <div
      className="group relative bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden hover:border-violet-500 transition-all duration-200 hover:shadow-lg hover:shadow-violet-900/20 cursor-pointer"
      onClick={() => onOpen(c.slug)}
    >
      {/* Iframe preview */}
      <div className="relative w-full h-44 overflow-hidden bg-zinc-950 pointer-events-none">
        <iframe
          src={`/cases/${c.slug}/index.html`}
          className="absolute top-0 left-0 border-0"
          style={{ width: '200%', height: '200%', transform: 'scale(0.5)', transformOrigin: 'top left' }}
          tabIndex={-1}
          loading="lazy"
          sandbox="allow-scripts allow-same-origin"
          title={c.title}
        />
        {/* Overlay so click registers on the card not iframe */}
        <div className="absolute inset-0 bg-transparent" />
      </div>

      {/* Info */}
      <div className="px-4 py-3 border-t border-zinc-800">
        <span className={`inline-block text-xs px-2 py-0.5 rounded-full border font-mono mb-2 ${CATEGORY_COLORS[c.category] || 'bg-zinc-800 text-zinc-400 border-zinc-700'}`}>
          {c.category}
        </span>
        <p className="text-sm font-semibold text-zinc-100 group-hover:text-violet-300 transition-colors mb-1">{c.title}</p>
        <p className="text-xs text-zinc-500 leading-relaxed">{c.desc}</p>
      </div>

      {/* View button on hover */}
      <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/40 rounded-xl">
        <span className="px-4 py-2 bg-violet-600 text-white text-sm font-semibold rounded-lg shadow-lg">
          Open Interactive ↗
        </span>
      </div>
    </div>
  );
}

function Modal({ slug, onClose }: { slug: string; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4" onClick={onClose}>
      <div className="relative w-full max-w-5xl h-[85vh] bg-zinc-950 rounded-xl overflow-hidden border border-zinc-700 shadow-2xl" onClick={e => e.stopPropagation()}>
        <button
          onClick={onClose}
          className="absolute top-3 right-3 z-10 w-8 h-8 flex items-center justify-center bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-full text-sm transition-colors"
        >
          ✕
        </button>
        <iframe
          src={`/cases/${slug}/index.html`}
          className="w-full h-full border-0"
          sandbox="allow-scripts allow-same-origin"
          title={slug}
        />
      </div>
    </div>
  );
}

export default function App() {
  const [openSlug, setOpenSlug] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 font-sans">

      {/* Nav */}
      <nav className="sticky top-0 z-40 border-b border-zinc-800 bg-zinc-950/90 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <span className="font-bold text-lg tracking-tight">
            <span className="text-violet-400">Vivi</span>Doc
          </span>
          <div className="flex items-center gap-6 text-sm text-zinc-400">
            <a href="https://arxiv.org/abs/2603.27991" target="_blank" rel="noopener" className="hover:text-zinc-100 transition-colors">Paper</a>
            <a href="https://github.com/MisterBrookT/vividoc" target="_blank" rel="noopener" className="hover:text-zinc-100 transition-colors">GitHub</a>
            <a
              href="https://vividoc-homepage-git-claude-repo-2aee21-misterbrookts-projects.vercel.app"
              target="_blank" rel="noopener"
              className="px-3 py-1.5 bg-violet-600 hover:bg-violet-500 text-white rounded-lg transition-colors font-medium"
            >
              About
            </a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-20 pb-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div>
            <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-violet-950 text-violet-300 border border-violet-800 mb-6">
              ACL 2026 · System Demonstrations
            </div>
            <h1 className="text-5xl font-bold tracking-tight leading-tight mb-5">
              Interactive documents,{' '}
              <span className="text-violet-400">generated from any topic.</span>
            </h1>
            <p className="text-zinc-400 text-lg leading-relaxed mb-8">
              ViviDoc turns a topic into a self-contained HTML document with explanatory text,
              math, and interactive visualizations — designed to make abstract concepts explorable.
            </p>
            <div className="flex flex-wrap gap-3">
              <a
                href="https://github.com/MisterBrookT/vividoc"
                target="_blank" rel="noopener"
                className="px-5 py-2.5 bg-violet-600 hover:bg-violet-500 text-white font-semibold rounded-lg transition-colors"
              >
                Try it (Claude Code)
              </a>
              <a
                href="https://arxiv.org/abs/2603.27991"
                target="_blank" rel="noopener"
                className="px-5 py-2.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-100 font-semibold rounded-lg transition-colors border border-zinc-700"
              >
                Read the paper
              </a>
            </div>
            <p className="text-zinc-600 text-sm mt-5 font-mono">
              /vividoc Fourier Transform
            </p>
          </div>

          {/* Featured demo */}
          <div
            className="relative rounded-xl overflow-hidden border border-zinc-700 shadow-2xl shadow-violet-950/30 cursor-pointer group"
            style={{ height: '420px' }}
            onClick={() => setOpenSlug('fourier_transform')}
          >
            <div className="w-full h-full pointer-events-none">
              <iframe
                src="/cases/fourier_transform/index.html"
                className="absolute top-0 left-0 border-0"
                style={{ width: '200%', height: '200%', transform: 'scale(0.5)', transformOrigin: 'top left' }}
                tabIndex={-1}
                sandbox="allow-scripts allow-same-origin"
                title="Fourier Transform demo"
              />
            </div>
            <div className="absolute inset-0 bg-transparent" />
            <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-zinc-950 to-transparent px-4 py-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-zinc-300">Fourier Transform</span>
                <span className="text-xs text-zinc-500 group-hover:text-violet-400 transition-colors">Click to interact →</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="border-y border-zinc-800 bg-zinc-900/50">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <h2 className="text-2xl font-bold text-center mb-12">How it works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { step: '01', title: 'Topic → SRTC Spec', desc: 'Claude reasons about the topic\'s character and designs custom interactions using the SRTC framework: State · Render · Transition · Constraint.' },
              { step: '02', title: 'Custom Style Design', desc: 'Each document gets a purpose-built visual style derived from the concept\'s emotional register, domain, and natural color associations.' },
              { step: '03', title: 'Self-contained HTML', desc: 'A single HTML file with KaTeX math, D3/Canvas visualizations, and fully interactive controls. Open directly in any browser.' },
            ].map(({ step, title, desc }) => (
              <div key={step} className="relative pl-16">
                <div className="absolute left-0 top-0 w-10 h-10 flex items-center justify-center rounded-lg bg-violet-950 border border-violet-800 text-violet-400 font-bold font-mono text-sm">
                  {step}
                </div>
                <h3 className="font-semibold text-zinc-100 mb-2">{title}</h3>
                <p className="text-zinc-500 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Gallery */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <div className="flex items-baseline justify-between mb-8">
          <h2 className="text-2xl font-bold">Example Gallery</h2>
          <span className="text-zinc-500 text-sm">8 interaction types · click any card to open</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {CASES.map(c => (
            <CaseCard key={c.slug} c={c} onOpen={setOpenSlug} />
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-800 py-10">
        <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4 text-zinc-600 text-sm">
          <span>ViviDoc · State Key Lab of CAD&CG, Zhejiang University</span>
          <div className="flex gap-6">
            <a href="https://arxiv.org/abs/2603.27991" target="_blank" rel="noopener" className="hover:text-zinc-400 transition-colors">arXiv 2603.27991</a>
            <a href="https://github.com/MisterBrookT/vividoc" target="_blank" rel="noopener" className="hover:text-zinc-400 transition-colors">GitHub</a>
          </div>
        </div>
      </footer>

      {/* Modal */}
      {openSlug && <Modal slug={openSlug} onClose={() => setOpenSlug(null)} />}
    </div>
  );
}
