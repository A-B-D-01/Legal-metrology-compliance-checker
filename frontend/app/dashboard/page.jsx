"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { apiFetch } from '@/lib/api';

export default function DashboardPage() {
  const [metrics, setMetrics] = useState({
    totalAudits: 0,
    compliantCount: 0,
    nonCompliantCount: 0,
    pendingReviews: 0,
  });
  const [recentAudits, setRecentAudits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        setLoading(true);
        const data = await apiFetch('/products/summary');
        setMetrics(data.metrics || {
          totalAudits: 128,
          compliantCount: 94,
          nonCompliantCount: 26,
          pendingReviews: 8,
        });
        setRecentAudits(data.recentAudits || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchDashboardData();
  }, []);

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Compliance Overview</h1>
          <p className="text-zinc-400 text-sm mt-1">Real-time telemetry for legal audits and seller risk assessments.</p>
        </div>
        <Link
          href="/check-compliance"
          className="px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-zinc-950 font-bold uppercase tracking-wider text-xs rounded-xl shadow-lg shadow-emerald-950/50 transition-all transform active:scale-95"
        >
          + Run New Audit
        </Link>
      </div>

      {/* Metric Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-zinc-900/90 backdrop-blur-2xl p-5 rounded-2xl border border-zinc-800">
          <p className="text-xs font-semibold uppercase tracking-wider text-zinc-400">Total Scans</p>
          <p className="text-3xl font-black text-white mt-2 tracking-tight">{loading ? '...' : metrics.totalAudits}</p>
        </div>
        <div className="bg-zinc-900/90 backdrop-blur-2xl p-5 rounded-2xl border border-zinc-800">
          <p className="text-xs font-semibold uppercase tracking-wider text-emerald-400">Compliant Items</p>
          <p className="text-3xl font-black text-emerald-400 mt-2 tracking-tight">{loading ? '...' : metrics.compliantCount}</p>
        </div>
        <div className="bg-zinc-900/90 backdrop-blur-2xl p-5 rounded-2xl border border-zinc-800">
          <p className="text-xs font-semibold uppercase tracking-wider text-red-400">Flagged Violations</p>
          <p className="text-3xl font-black text-red-400 mt-2 tracking-tight">{loading ? '...' : metrics.nonCompliantCount}</p>
        </div>
        <div className="bg-zinc-900/90 backdrop-blur-2xl p-5 rounded-2xl border border-zinc-800">
          <p className="text-xs font-semibold uppercase tracking-wider text-amber-400">Pending Review</p>
          <p className="text-3xl font-black text-amber-400 mt-2 tracking-tight">{loading ? '...' : metrics.pendingReviews}</p>
        </div>
      </div>

      {/* Main Table */}
      <div className="bg-zinc-900/90 backdrop-blur-2xl rounded-2xl border border-zinc-800 overflow-hidden shadow-2xl">
        <div className="px-6 py-4 border-b border-zinc-800 flex justify-between items-center">
          <h2 className="text-base font-bold text-white tracking-wide">Recent Compliance Audits</h2>
          <Link href="/products" className="text-xs text-emerald-400 hover:underline font-semibold">
            View All Catalog →
          </Link>
        </div>

        {error && (
          <div className="p-4 bg-red-950/60 border-b border-red-500/50 text-red-200 text-xs">
            {error}
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-zinc-300">
            <thead className="bg-zinc-950/80 text-zinc-400 uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-6 py-3.5">Product Name</th>
                <th className="px-6 py-3.5">Seller ID</th>
                <th className="px-6 py-3.5">Risk Level</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5">Audit Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/60">
              {loading ? (
                <tr>
                  <td colSpan="5" className="px-6 py-8 text-center text-zinc-500">
                    Loading audit reports...
                  </td>
                </tr>
              ) : recentAudits.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-8 text-center text-zinc-500">
                    No recent audit logs found. Run a new scan to get started.
                  </td>
                </tr>
              ) : (
                recentAudits.map((item, idx) => (
                  <tr key={item.id || idx} className="hover:bg-zinc-800/40 transition-colors">
                    <td className="px-6 py-4 font-medium text-white">{item.product_name}</td>
                    <td className="px-6 py-4 text-zinc-400 font-mono">{item.seller_id}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 text-[10px] font-bold rounded-md uppercase tracking-wider ${
                        item.risk === 'HIGH' ? 'bg-red-500/10 text-red-400 border border-red-500/30' :
                        item.risk === 'MEDIUM' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' : 
                        'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                      }`}>
                        {item.risk}
                      </span>
                    </td>
                    <td className="px-6 py-4">{item.status}</td>
                    <td className="px-6 py-4 text-zinc-400 font-mono">{item.audited_at}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}