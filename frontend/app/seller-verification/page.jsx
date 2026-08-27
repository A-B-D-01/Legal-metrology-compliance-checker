"use client";

import { useState } from 'react';
import { apiFetch } from '@/lib/api';

export default function SellerVerificationPage() {
  const [sellerId, setSellerId] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!sellerId.trim() || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await apiFetch(`/sellers/verify?seller_id=${encodeURIComponent(sellerId)}`);
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
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">Seller Verification</h1>
        <p className="text-slate-600 dark:text-zinc-400 text-sm mt-1">Audit merchant credibility, history, and legal registration numbers.</p>
      </div>

      {/* Input Card */}
      <div className="bg-white dark:bg-zinc-900/90 backdrop-blur-2xl p-6 rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-xl dark:shadow-[0_0_50px_rgba(0,0,0,0.8)] relative">
        <div className="absolute top-0 left-1/3 w-32 h-[2px] bg-gradient-to-r from-transparent via-emerald-500 to-transparent" />
        <form onSubmit={handleVerify} className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            required
            placeholder="Enter Seller ID or License Number..."
            value={sellerId}
            onChange={(e) => setSellerId(e.target.value)}
            className="flex-1 px-4 py-3 bg-slate-100 dark:bg-zinc-950 border border-slate-300 dark:border-zinc-800 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-600 focus:outline-none focus:border-emerald-500 text-sm transition-all"
          />
          <button
            type="submit"
            disabled={loading || !sellerId.trim()}
            className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white dark:text-zinc-950 font-bold uppercase tracking-wider text-xs rounded-xl shadow-md transition-all active:scale-95 disabled:opacity-50 whitespace-nowrap"
          >
            {loading ? 'Validating...' : 'Verify Merchant'}
          </button>
        </form>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-500/50 text-red-700 dark:text-red-200 text-xs rounded-2xl shadow-sm">
          {error}
        </div>
      )}

      {/* Result Card */}
      {result && (
        <div className="bg-white dark:bg-zinc-900/90 backdrop-blur-2xl p-6 rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-xl space-y-6">
          <div className="flex justify-between items-center border-b border-slate-200 dark:border-zinc-800 pb-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white tracking-wide">
                {result.seller_name || 'Merchant Entity Record'}
              </h2>
              <p className="text-xs font-mono text-slate-500 dark:text-zinc-500 mt-0.5">ID: {sellerId}</p>
            </div>
            <span
              className={`px-3 py-1 text-xs font-bold rounded-full uppercase tracking-wider ${
                result.is_verified
                  ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
                  : 'bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/30'
              }`}
            >
              {result.is_verified ? 'VERIFIED SELLER' : 'UNVERIFIED / RISKY'}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="bg-slate-50 dark:bg-zinc-950 p-4 rounded-xl border border-slate-200 dark:border-zinc-800">
              <span className="text-slate-500 dark:text-zinc-500 uppercase font-semibold text-[10px] tracking-wider block">Trust Score</span>
              <span className="text-2xl font-black text-slate-900 dark:text-white mt-1 block">
                {result.trust_score !== undefined ? `${result.trust_score} / 100` : 'N/A'}
              </span>
            </div>
            <div className="bg-slate-50 dark:bg-zinc-950 p-4 rounded-xl border border-slate-200 dark:border-zinc-800">
              <span className="text-slate-500 dark:text-zinc-500 uppercase font-semibold text-[10px] tracking-wider block">Active Listings</span>
              <span className="text-2xl font-black text-slate-900 dark:text-white mt-1 block">
                {result.total_listings || 0}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}