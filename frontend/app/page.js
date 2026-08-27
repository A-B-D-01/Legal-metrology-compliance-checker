import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[75vh] text-center space-y-8 max-w-4xl mx-auto px-4">
      {/* Badge */}
      <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 bg-emerald-500/10 border border-emerald-500/30 rounded-full text-xs font-semibold text-emerald-600 dark:text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.12)]">
        <span>⚡ AI-Powered Legal Metrology Checker</span>
      </div>

      {/* Main Heading */}
      <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white">
        Automated E-Commerce{' '}
        <span className="bg-gradient-to-r from-emerald-600 via-teal-500 to-cyan-600 dark:from-emerald-400 dark:via-teal-300 dark:to-cyan-400 bg-clip-text text-transparent">
          Compliance & Verification
        </span>
      </h1>

      {/* Description */}
      <p className="text-lg text-slate-600 dark:text-zinc-400 max-w-2xl leading-relaxed">
        Scan product listings, perform OCR text extraction on packaging labels, and query regulatory guidelines in real-time using FAISS RAG and Gemini AI.
      </p>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 w-full justify-center pt-2">
        <Link
          href="/check-compliance"
          className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white dark:text-zinc-950 font-bold rounded-xl shadow-md transition-all text-xs uppercase tracking-wider active:scale-95 flex items-center justify-center gap-2"
        >
          Run Compliance Check 
        </Link>
        <Link
          href="/dashboard"
          className="px-6 py-3 bg-slate-100 hover:bg-slate-200 dark:bg-zinc-900/80 dark:hover:bg-zinc-800 border border-slate-300 dark:border-zinc-800 text-slate-800 dark:text-zinc-200 font-semibold rounded-xl transition-all text-xs uppercase tracking-wider hover:border-slate-400 dark:hover:border-zinc-700 flex items-center justify-center"
        >
          View Dashboard
        </Link>
      </div>

      {/* Feature Highlights Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-10 w-full text-left">
        <div className="p-5 bg-slate-50 dark:bg-zinc-950/60 border border-slate-200 dark:border-zinc-800/80 rounded-2xl hover:border-slate-300 dark:hover:border-zinc-700 transition-colors shadow-sm">
          <div className="text-2xl mb-3">📸</div>
          <h3 className="font-bold text-slate-900 dark:text-white text-sm tracking-wide">Vision OCR</h3>
          <p className="text-xs text-slate-600 dark:text-zinc-400 mt-1.5 leading-relaxed">Extract text directly from product packaging images and PDF files.</p>
        </div>
        <div className="p-5 bg-slate-50 dark:bg-zinc-950/60 border border-slate-200 dark:border-zinc-800/80 rounded-2xl hover:border-slate-300 dark:hover:border-zinc-700 transition-colors shadow-sm">
          <div className="text-2xl mb-3">🔎</div>
          <h3 className="font-bold text-slate-900 dark:text-white text-sm tracking-wide">Automated Scraping</h3>
          <p className="text-xs text-slate-600 dark:text-zinc-400 mt-1.5 leading-relaxed">Scrape e-commerce listings using Selenium integration.</p>
        </div>
        <div className="p-5 bg-slate-50 dark:bg-zinc-950/60 border border-slate-200 dark:border-zinc-800/80 rounded-2xl hover:border-slate-300 dark:hover:border-zinc-700 transition-colors shadow-sm">
          <div className="text-2xl mb-3">🤖</div>
          <h3 className="font-bold text-slate-900 dark:text-white text-sm tracking-wide">FAISS Vector RAG</h3>
          <p className="text-xs text-slate-600 dark:text-zinc-400 mt-1.5 leading-relaxed">Cross-check findings against statutory legal compliance rules.</p>
        </div>
      </div>
    </div>
  );
}