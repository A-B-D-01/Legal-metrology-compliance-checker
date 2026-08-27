"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { apiFetch } from '@/lib/api';

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [filterRisk, setFilterRisk] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchProducts() {
      try {
        setLoading(true);
        setError(null);
        const data = await apiFetch('/products');
        setProducts(data.products || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchProducts();
  }, []);

  const filteredProducts = products.filter((p) => {
    const matchesSearch =
      p.title?.toLowerCase().includes(search.toLowerCase()) ||
      p.seller_id?.toLowerCase().includes(search.toLowerCase());
    const matchesRisk = filterRisk === 'ALL' || p.risk_level === filterRisk;
    return matchesSearch && matchesRisk;
  });

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">Product Catalog</h1>
        <p className="text-slate-600 dark:text-zinc-400 text-sm mt-1">Manage, filter, and audit all indexed marketplace listings.</p>
      </div>

      {/* Control Bar: Filters & Search */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between bg-white dark:bg-zinc-900/90 backdrop-blur-2xl p-4 rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-xl">
        <div className="relative flex-1">
          <input
            type="text"
            placeholder="Search by product name or seller ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full px-4 py-2.5 bg-slate-100 dark:bg-zinc-950 border border-slate-300 dark:border-zinc-800 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-600 text-sm focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/20 transition-all"
          />
        </div>

        <select
          value={filterRisk}
          onChange={(e) => setFilterRisk(e.target.value)}
          className="px-4 py-2.5 bg-slate-100 dark:bg-zinc-950 border border-slate-300 dark:border-zinc-800 rounded-xl text-slate-700 dark:text-zinc-300 text-sm focus:outline-none focus:border-emerald-500 transition-all cursor-pointer"
        >
          <option value="ALL">All Risk Levels</option>
          <option value="LOW">Low Risk</option>
          <option value="MEDIUM">Medium Risk</option>
          <option value="HIGH">High Risk</option>
        </select>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-500/50 text-red-700 dark:text-red-200 text-xs rounded-2xl shadow-sm">
          {error}
        </div>
      )}

      {/* Grid Content */}
      {loading ? (
        <div className="text-center py-16 text-slate-500 dark:text-zinc-500 text-sm flex items-center justify-center gap-2">
          <span className="w-2 h-2 bg-emerald-500 dark:bg-emerald-400 rounded-full animate-ping" />
          <span>Fetching product index...</span>
        </div>
      ) : filteredProducts.length === 0 ? (
        <div className="text-center py-16 text-slate-500 dark:text-zinc-500 bg-slate-50 dark:bg-zinc-900/50 rounded-2xl border border-slate-200 dark:border-zinc-800/80 text-sm">
          No catalog items match your specified filter parameters.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((item, idx) => (
            <div
              key={item.id || idx}
              className="bg-white dark:bg-zinc-900/90 backdrop-blur-2xl rounded-2xl border border-slate-200 dark:border-zinc-800 p-5 flex flex-col justify-between hover:border-slate-300 dark:hover:border-zinc-700 transition-all duration-200 shadow-md group relative overflow-hidden"
            >
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span
                    className={`px-2.5 py-1 text-[10px] font-bold rounded-md uppercase tracking-wider ${
                      item.risk_level === 'HIGH'
                        ? 'bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/30'
                        : item.risk_level === 'MEDIUM'
                        ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30'
                        : 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
                    }`}
                  >
                    {item.risk_level || 'LOW'} RISK
                  </span>
                  <span className="text-[11px] font-mono text-slate-500 dark:text-zinc-500">ID: {item.seller_id}</span>
                </div>

                <h3 className="text-base font-bold text-slate-900 dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors line-clamp-1">
                  {item.title}
                </h3>
                <p className="text-xs text-slate-600 dark:text-zinc-400 leading-relaxed line-clamp-2">
                  {item.description || 'No description logged.'}
                </p>
              </div>

              <div className="pt-4 mt-4 border-t border-slate-100 dark:border-zinc-800/80 flex justify-between items-center text-xs text-slate-500 dark:text-zinc-500">
                <span className="font-mono text-[11px]">{item.last_audited || 'Recently Audited'}</span>
                <Link
                  href={`/check-compliance?url=${encodeURIComponent(item.url || '')}`}
                  className="text-emerald-600 dark:text-emerald-400 hover:text-emerald-500 dark:hover:text-emerald-300 font-semibold transition-colors text-xs flex items-center gap-1"
                >
                  Re-audit <span className="text-sm">→</span>
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}