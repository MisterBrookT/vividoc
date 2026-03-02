import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { examples } from "../config/examples";

export default function ExamplePage() {
  const { slug } = useParams<{ slug: string }>();
  const example = examples.find((e) => e.slug === slug);
  const [tab, setTab] = useState<"vividoc" | "baseline">("vividoc");

  if (!example) {
    return (
      <main className="max-w-[900px] mx-auto px-6 py-20 text-center font-[Inter,sans-serif]">
        <p className="text-slate-500">Example not found.</p>
        <Link to="/" className="text-indigo-600 text-sm mt-4 inline-block">← Back</Link>
      </main>
    );
  }

  return (
    <main className="h-screen flex flex-col font-[Inter,sans-serif]">
      {/* Top bar */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-slate-200 bg-white shrink-0">
        <div className="flex items-center gap-4">
          <Link to="/" className="text-slate-400 hover:text-indigo-600 text-sm transition-colors no-underline">
            ← Back
          </Link>
          <div>
            <h1 className="text-sm font-semibold text-slate-700">{example.title}</h1>
            <p className="text-xs text-slate-400">{example.field}</p>
          </div>
        </div>
        <div className="flex rounded-lg border border-slate-200 overflow-hidden">
          <button
            onClick={() => setTab("vividoc")}
            className={`px-4 py-1.5 text-xs font-medium transition-colors cursor-pointer ${
              tab === "vividoc"
                ? "bg-indigo-600 text-white"
                : "bg-white text-slate-500 hover:text-indigo-600"
            }`}
          >
            ViviDoc
          </button>
          <button
            onClick={() => setTab("baseline")}
            className={`px-4 py-1.5 text-xs font-medium transition-colors cursor-pointer ${
              tab === "baseline"
                ? "bg-indigo-600 text-white"
                : "bg-white text-slate-500 hover:text-indigo-600"
            }`}
          >
            Baseline
          </button>
        </div>
      </div>

      {/* iframe */}
      <iframe
        key={tab}
        src={`/examples/${slug}/${tab}.html`}
        className="flex-1 w-full border-0"
        title={`${example.title} - ${tab}`}
        sandbox="allow-scripts allow-same-origin"
      />
    </main>
  );
}
