"use client";

import { useState } from 'react';
import { apiFetch } from '@/lib/api';

export default function CheckCompliancePage() {
  const [inputType, setInputType] = useState('url'); // 'url' or 'file'
  const [url, setUrl] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleTypeSwitch = (type) => {
    setInputType(type);
    setError(null);
    setResult(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let payload;
      let headers = {};

      if (inputType === 'url') {
        payload = JSON.stringify({ target_url: url });
        headers['Content-Type'] = 'application/json';
      } else {
        if (!file) throw new Error('Please select an image or document to upload.');
        const formData = new FormData();
        formData.append('file', file);
        payload = formData;
      }

      const data = await apiFetch('/compliance/analyze', {
        method: 'POST',
        headers,
        body: payload,
      });

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">Audit Engine</h1>
        <p className="text-slate-600 dark:text-zinc-400 text-sm mt-1">Run automated OCR label extraction, web scraping, and RAG risk evaluations.</p>
      </div>

      {/* Form Card */}
      <div className="bg-white dark:bg-zinc-900/90 backdrop-blur-2xl p-6 rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-xl dark:shadow-[0_0_50px_rgba(0,0,0,0.8)] relative">
        <div className="absolute top-0 left-1/4 w-32 h-[2px] bg-gradient-to-r from-transparent via-cyan-500 to-transparent" />
        
        <div className="flex border-b border-slate-200 dark:border-zinc-800 pb-4 mb-6">
          <button
            type="button"
            onClick={() => handleTypeSwitch('url')}
            className={`px-4 py-2 text-xs font-semibold uppercase tracking-wider rounded-lg transition-all ${
              inputType === 'url' 
                ? 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30' 
                : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Listing URL Scraper
          </button>
          <button
            type="button"
            onClick={() => handleTypeSwitch('file')}
            className={`ml-3 px-4 py-2 text-xs font-semibold uppercase tracking-wider rounded-lg transition-all ${
              inputType === 'file' 
                ? 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30' 
                : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Label Image / PDF OCR
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {inputType === 'url' ? (
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-zinc-400 mb-2">Product Target URL</label>
              <input
                type="url"
                required
                placeholder="https://ecommerce.com/product/123"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="w-full px-4 py-3 bg-slate-100 dark:bg-zinc-950 border border-slate-300 dark:border-zinc-800 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-600 focus:outline-none focus:border-cyan-500 text-sm transition-all"
              />
            </div>
          ) : (
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-zinc-400 mb-2">Packaging Image or Legal PDF Document</label>
              <input
                type="file"
                accept="image/*,.pdf"
                required
                onChange={(e) => setFile(e.target.files[0])}
                className="w-full text-xs text-slate-600 dark:text-zinc-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:bg-slate-200 dark:file:bg-zinc-800 file:text-cyan-600 dark:file:text-cyan-400 hover:file:bg-slate-300 dark:hover:file:bg-zinc-700 cursor-pointer border border-slate-300 dark:border-zinc-800 rounded-xl bg-slate-100 dark:bg-zinc-950 p-1"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 text-white dark:text-zinc-950 font-bold uppercase tracking-wider text-xs rounded-xl shadow-md transition-all active:scale-[0.98] disabled:opacity-50"
          >
            {loading ? 'Executing AI Compliance Pipeline...' : 'Run Automated Audit'}
          </button>
        </form>
      </div>

      {/* Error View */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-500/50 text-red-700 dark:text-red-200 text-xs rounded-2xl shadow-sm">
          {error}
        </div>
      )}

      {/* Results View */}
      {result && (
        <div className="bg-white dark:bg-zinc-900/90 backdrop-blur-2xl p-6 rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-xl space-y-4">
          <div className="flex justify-between items-center border-b border-slate-200 dark:border-zinc-800 pb-4">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white tracking-wide">Audit Report</h2>
            <span className={`px-3 py-1 text-xs font-bold rounded-full uppercase tracking-wider ${
              result.status === 'COMPLIANT' 
                ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30' 
                : 'bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/30'
            }`}>
              {result.status || 'NON-COMPLIANT'}
            </span>
          </div>
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-zinc-400 mb-2">Findings Summary</h3>
            <p className="text-slate-800 dark:text-zinc-300 text-sm whitespace-pre-wrap leading-relaxed">{result.summary}</p>
          </div>
        </div>
      )}
    </div>
  );
}