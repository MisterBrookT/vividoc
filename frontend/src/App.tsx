import { useState } from 'react';

/* ── Palette ── */
const css = `
  :root {
    --bg:      #0a0908;
    --card:    #111009;
    --card-hv: #18160f;
    --border:  #252219;
    --accent:  #c8961e;
    --gold:    #e5b84a;
    --text:    #f0e6d3;
    --muted:   #6d6254;
    --dim:     #9e9080;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body { background: var(--bg); color: var(--text); }
  ::selection { background: rgba(200,150,30,0.3); }
  /* Scrollbar */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
`;

/* ── Data ── */
const CASES = [
  { slug: 'fourier_transform',    title: 'Fourier Transform',      domain: 'Physics & Math',      category: 'Temporal Control',      desc: 'Signal decomposition, Gibbs phenomenon, epicycles.' },
  { slug: 'lorenz_attractor',     title: 'Lorenz Attractor',       domain: 'Physics & Math',      category: 'Parameter Exploration', desc: 'Deterministic chaos and the butterfly effect.' },
  { slug: 'action_potential',     title: 'Action Potential',       domain: 'Biology',             category: 'Temporal Control',      desc: 'Ion channels, threshold dynamics, and the all-or-nothing law.' },
  { slug: 'dna_replication',      title: 'DNA Replication',        domain: 'Biology',             category: 'Temporal Control',      desc: 'Helicase unwinds, polymerase copies — fidelity down to one error per billion bases.' },
  { slug: 'gradient_descent',     title: 'Gradient Descent',       domain: 'Machine Learning',    category: 'Direct Manipulation',   desc: 'Click to place the starting point on a 3D loss surface and watch SGD, momentum, and Adam navigate to minima.' },
  { slug: 'bias_variance',        title: 'Bias–Variance Tradeoff', domain: 'Machine Learning',    category: 'Parameter Exploration', desc: 'Fit polynomials to noisy data — as degree grows, watch bias collapse and variance explode into overfitting.' },
  { slug: 'shannon_entropy',      title: 'Shannon Entropy',        domain: 'Information Theory',  category: 'Parameter Exploration', desc: 'Adjust symbol probabilities and watch entropy peak at maximum uncertainty — the mathematical surprise.' },
  { slug: 'huffman_coding',       title: 'Huffman Coding',         domain: 'Information Theory',  category: 'Freeform Construction', desc: 'Edit symbol frequencies and watch the optimal prefix-free tree rebuild itself to minimize average code length.' },
];

const CATEGORY_DOT: Record<string, string> = {
  'Temporal Control':       '#f472b6',
  'Parameter Exploration':  '#22d3ee',
  'Direct Manipulation':    '#10b981',
  'Freeform Construction':  '#f59e0b',
  'State Switching':        '#60a5fa',
  'Inspection':             '#a78bfa',
  'Spatial Navigation':     '#38bdf8',
  'Scroll-driven Narrative':'#f87171',
};

/* ── Sub-components ── */
function CaseCard({ c, onOpen }: { c: { slug: string; title: string; domain: string; category: string; desc: string }; onOpen: (s: string) => void }) {
  return (
    <div
      onClick={() => onOpen(c.slug)}
      style={{
        background: 'var(--card)',
        border: '1px solid var(--border)',
        borderRadius: 8,
        overflow: 'hidden',
        cursor: 'pointer',
        transition: 'border-color 0.2s, transform 0.2s, box-shadow 0.2s',
      }}
      onMouseEnter={e => {
        (e.currentTarget as HTMLElement).style.borderColor = 'var(--accent)';
        (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
        (e.currentTarget as HTMLElement).style.boxShadow = '0 8px 32px rgba(200,150,30,0.12)';
      }}
      onMouseLeave={e => {
        (e.currentTarget as HTMLElement).style.borderColor = 'var(--border)';
        (e.currentTarget as HTMLElement).style.transform = 'none';
        (e.currentTarget as HTMLElement).style.boxShadow = 'none';
      }}
    >
      {/* iframe preview */}
      <div style={{ position: 'relative', height: 150, overflow: 'hidden', background: '#080706', pointerEvents: 'none' }}>
        <iframe
          src={`/cases/${c.slug}/index.html`}
          style={{ position: 'absolute', top: 0, left: 0, width: '200%', height: '200%', transform: 'scale(0.5)', transformOrigin: 'top left', border: 'none' }}
          tabIndex={-1}
          loading="lazy"
          sandbox="allow-scripts allow-same-origin"
          title={c.title}
        />
        <div style={{ position: 'absolute', inset: 0 }} />
      </div>

      {/* Info */}
      <div style={{ padding: '11px 13px 13px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 5 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <span style={{
              width: 5, height: 5, borderRadius: '50%',
              background: CATEGORY_DOT[c.category] || '#888',
              flexShrink: 0,
            }} />
            <span style={{ fontSize: 10, color: 'var(--dim)', fontFamily: 'Inter, sans-serif', letterSpacing: '0.05em' }}>
              {c.category}
            </span>
          </div>
          <span style={{ fontSize: 10, color: 'var(--muted)', fontFamily: 'Inter, sans-serif', opacity: 0.7 }}>
            {c.domain}
          </span>
        </div>
        <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--text)', fontFamily: 'Inter, sans-serif', marginBottom: 3, lineHeight: 1.3 }}>
          {c.title}
        </p>
        <p style={{ fontSize: 11, color: 'var(--muted)', fontFamily: 'Inter, sans-serif', lineHeight: 1.55 }}>
          {c.desc}
        </p>
      </div>
    </div>
  );
}

function Modal({ slug, onClose }: { slug: string; onClose: () => void }) {
  return (
    <div
      style={{ position: 'fixed', inset: 0, zIndex: 50, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.85)', padding: 16 }}
      onClick={onClose}
    >
      <div
        style={{ position: 'relative', width: '100%', maxWidth: 1100, height: '88vh', background: '#09080a', borderRadius: 10, overflow: 'hidden', border: '1px solid var(--border)' }}
        onClick={e => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: 12, right: 12, zIndex: 10, width: 32, height: 32, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(255,255,255,0.08)', border: 'none', borderRadius: '50%', color: 'var(--dim)', cursor: 'pointer', fontSize: 16 }}
        >✕</button>
        <iframe src={`/cases/${slug}/index.html`} style={{ width: '100%', height: '100%', border: 'none' }} sandbox="allow-scripts allow-same-origin" title={slug} />
      </div>
    </div>
  );
}

/* ── Main ── */
export default function App() {
  const [openSlug, setOpenSlug] = useState<string | null>(null);

  return (
    <>
      <style>{css}</style>

      {/* Nav */}
      <nav style={{
        position: 'sticky', top: 0, zIndex: 40,
        borderBottom: '1px solid var(--border)',
        background: 'rgba(10,9,8,0.92)',
        backdropFilter: 'blur(12px)',
      }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px', height: 56, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontFamily: "'Playfair Display', serif", fontWeight: 700, fontSize: 20, color: 'var(--text)', letterSpacing: '0.02em' }}>
            Vivi<span style={{ color: 'var(--gold)' }}>Doc</span>
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 28 }}>
            {[
              { label: 'Paper', href: 'https://arxiv.org/abs/2603.27991' },
              { label: 'GitHub', href: 'https://github.com/MisterBrookT/vividoc' },
            ].map(({ label, href }) => (
              <a key={label} href={href} target="_blank" rel="noopener"
                style={{ fontSize: 14, color: 'var(--dim)', textDecoration: 'none', fontFamily: 'Inter, sans-serif', transition: 'color 0.15s' }}
                onMouseEnter={e => (e.currentTarget.style.color = 'var(--text)')}
                onMouseLeave={e => (e.currentTarget.style.color = 'var(--dim)')}
              >{label}</a>
            ))}
            <a href="https://github.com/MisterBrookT/vividoc" target="_blank" rel="noopener"
              style={{ padding: '6px 18px', background: 'var(--accent)', color: '#0a0908', borderRadius: 6, fontSize: 13, fontWeight: 600, fontFamily: 'Inter, sans-serif', textDecoration: 'none', transition: 'background 0.15s' }}
              onMouseEnter={e => (e.currentTarget.style.background = 'var(--gold)')}
              onMouseLeave={e => (e.currentTarget.style.background = 'var(--accent)')}
            >Try it</a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section style={{ maxWidth: 1200, margin: '0 auto', padding: '100px 32px 80px' }}>
        <p style={{ fontFamily: 'Inter, sans-serif', fontSize: 12, letterSpacing: '0.15em', color: 'var(--accent)', textTransform: 'uppercase', marginBottom: 24 }}>
          Interactive Document Generation
        </p>
        <h1 style={{
          fontFamily: "'Playfair Display', serif",
          fontSize: 'clamp(3rem, 7vw, 5.5rem)',
          fontWeight: 900,
          lineHeight: 1.08,
          color: 'var(--text)',
          maxWidth: 800,
          marginBottom: 28,
        }}>
          Make any topic<br />
          <span style={{ color: 'var(--gold)', fontStyle: 'italic' }}>explorable.</span>
        </h1>
        <p style={{ fontFamily: 'Inter, sans-serif', fontSize: 17, color: 'var(--dim)', maxWidth: 560, lineHeight: 1.75, marginBottom: 40 }}>
          ViviDoc turns a topic into a self-contained HTML document with explanatory
          text, math, and interactive visualizations — designed to make abstract concepts hands-on.
        </p>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 60 }}>
          <a href="https://github.com/MisterBrookT/vividoc" target="_blank" rel="noopener"
            style={{ padding: '12px 28px', background: 'var(--accent)', color: '#0a0908', borderRadius: 6, fontSize: 14, fontWeight: 600, fontFamily: 'Inter, sans-serif', textDecoration: 'none' }}>
            Get started on GitHub ↗
          </a>
          <a href="https://arxiv.org/abs/2603.27991" target="_blank" rel="noopener"
            style={{ padding: '12px 28px', background: 'transparent', color: 'var(--dim)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 14, fontFamily: 'Inter, sans-serif', textDecoration: 'none' }}>
            arXiv 2603.27991
          </a>
        </div>
        {/* How it works — inline */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 1, borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)', padding: '32px 0' }}>
          {[
            { n: '01', t: 'SRTC Interaction Spec', d: 'Claude reasons about your topic and designs custom interactions: State · Render · Transition · Constraint.' },
            { n: '02', t: 'Purpose-built style',   d: 'Each document gets a visual identity derived from the concept\'s emotional register and domain.' },
            { n: '03', t: 'One HTML file',          d: 'KaTeX math, canvas visualizations, interactive controls. Open in any browser, no server.' },
          ].map(({ n, t, d }) => (
            <div key={n} style={{ padding: '0 24px 0 0' }}>
              <span style={{ fontFamily: 'Inter, sans-serif', fontSize: 11, color: 'var(--accent)', letterSpacing: '0.1em' }}>{n}</span>
              <p style={{ fontFamily: 'Inter, sans-serif', fontWeight: 600, color: 'var(--text)', fontSize: 13, marginTop: 8, marginBottom: 8 }}>{t}</p>
              <p style={{ fontFamily: 'Inter, sans-serif', fontSize: 12, color: 'var(--muted)', lineHeight: 1.7 }}>{d}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Cases grid — flat 4-column layout */}
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px 100px' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: 16,
        }}>
          {CASES.map(c => (
            <CaseCard key={c.slug} c={c} onOpen={setOpenSlug} />
          ))}
        </div>
      </div>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--border)', padding: '32px 0' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <span style={{ fontFamily: 'Inter, sans-serif', fontSize: 12, color: 'var(--muted)' }}>
            ViviDoc · <em>ACL 2026 System Demonstrations</em> · <a href="https://arxiv.org/abs/2603.27991" target="_blank" rel="noopener" style={{ color: 'var(--muted)', textDecoration: 'none' }}>arXiv:2603.27991</a>
          </span>
          <a href="https://github.com/MisterBrookT/vividoc" target="_blank" rel="noopener"
            style={{ fontFamily: 'Inter, sans-serif', fontSize: 12, color: 'var(--muted)', textDecoration: 'none' }}>
            GitHub ↗
          </a>
        </div>
      </footer>

      {openSlug && <Modal slug={openSlug} onClose={() => setOpenSlug(null)} />}
    </>
  );
}
