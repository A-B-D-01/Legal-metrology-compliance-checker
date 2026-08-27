import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[75vh] text-center space-y-8 max-w-3xl mx-auto">
      {/* Badge */}
      <div className="inline-flex items-center space-x-2 px-3 py-1 bg-blue-900/40 border border-blue-500/30 rounded-full text-xs font-semibold text-blue-400">
        <span>⚡ AI-Powered Legal Metrology Checker</span>
      </div>

      {/* Main Heading */}
      <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white">
        Automated E-Commerce{' '}
        <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
          Compliance & Verification
        </span>
      </h1>

      {/* Description */}
      <p className="text-lg text-slate-300 max-w-2xl">
        Scan product listings, perform OCR text extraction on packaging labels, and query regulatory guidelines in real-time using FAISS RAG and Gemini AI.
      </p>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 w-full justify-center">
        <Link
          href="/check-compliance"
          className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl shadow-lg shadow-blue-600/25 transition-all text-sm"
        >
          Run Compliance Check 
        </Link>
        <Link
          href="/dashboard"
          className="px-6 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-medium rounded-xl transition-all text-sm"
        >
          View Dashboard
        </Link>
      </div>

      {/* Feature Highlights Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-12 w-full text-left">
        <div className="p-4 bg-slate-800/50 border border-slate-700/60 rounded-xl">
          <div className="text-xl mb-2">📸</div>
          <h3 className="font-semibold text-white text-sm">Vision OCR</h3>
          <p className="text-xs text-slate-400 mt-1">Extract text directly from product packaging images and PDF files.</p>
        </div>
        <div className="p-4 bg-slate-800/50 border border-slate-700/60 rounded-xl">
          <div className="text-xl mb-2">🔎</div>
          <h3 className="font-semibold text-white text-sm">Automated Scraping</h3>
          <p className="text-xs text-slate-400 mt-1">Scrape e-commerce listings using Selenium integration.</p>
        </div>
        <div className="p-4 bg-slate-800/50 border border-slate-700/60 rounded-xl">
          <div className="text-xl mb-2">🤖</div>
          <h3 className="font-semibold text-white text-sm">FAISS Vector RAG</h3>
          <p className="text-xs text-slate-400 mt-1">Cross-check findings against statutory legal compliance rules.</p>
        </div>
      </div>
    </div>
  );
}