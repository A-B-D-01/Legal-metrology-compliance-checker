"use client";

import { useState, useEffect } from 'react';
import { apiFetch } from '@/lib/api';

export default function RewardsPage() {
  const [stats, setStats] = useState({
    points: 450,
    rank: 'Gold Auditor',
    auditsCompleted: 38,
    accuracyRate: '98.4%',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchRewards() {
      try {
        const data = await apiFetch('/rewards');
        if (data) setStats(data);
      } catch (err) {
        // Fallback to initial local stats if endpoint isn't wired yet
      } finally {
        setLoading(false);
      }
    }
    fetchRewards();
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">Auditor Rewards</h1>
        <p className="text-slate-600 dark:text-zinc-400 text-sm mt-1">
          Track community verification metrics, unlock badges, and earn trust tier status.
        </p>
      </div>

      {/* Rewards Telemetry Grid */}
      <div className="bg-gradient-to-r from-white via-slate-50 to-white dark:from-zinc-900 dark:via-zinc-900/90 dark:to-zinc-950 p-6 rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-xl dark:shadow-[0_0_50px_rgba(0,0,0,0.8)] grid grid-cols-2 md:grid-cols-4 gap-6 text-center relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-emerald-500 via-teal-500 to-transparent opacity-60" />

        <div className="p-2">
          <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500 dark:text-zinc-400">Total Points</span>
          <p className="text-3xl font-black text-emerald-600 dark:text-emerald-400 mt-2 tracking-tight">
            {loading ? '...' : stats.points}
          </p>
        </div>
        <div className="p-2">
          <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500 dark:text-zinc-400">Current Tier</span>
          <p className="text-lg font-bold text-amber-600 dark:text-amber-400 mt-3 tracking-wide">{loading ? '...' : stats.rank}</p>
        </div>
        <div className="p-2">
          <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500 dark:text-zinc-400">Audits Done</span>
          <p className="text-3xl font-black text-slate-900 dark:text-white mt-2 tracking-tight">
            {loading ? '...' : stats.auditsCompleted}
          </p>
        </div>
        <div className="p-2">
          <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500 dark:text-zinc-400">Accuracy</span>
          <p className="text-3xl font-black text-teal-600 dark:text-teal-400 mt-2 tracking-tight">
            {loading ? '...' : stats.accuracyRate}
          </p>
        </div>
      </div>

      {/* Unlocked Achievements */}
      <div className="bg-white dark:bg-zinc-900/90 backdrop-blur-2xl p-6 rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-xl space-y-5">
        <h2 className="text-base font-bold text-slate-900 dark:text-white tracking-wide">Unlocked Achievements</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-slate-50 dark:bg-zinc-950 p-4 rounded-xl border border-slate-200 dark:border-zinc-800 flex items-start space-x-3.5 hover:border-slate-300 dark:hover:border-zinc-700 transition-colors">
            <span className="text-2xl p-2 bg-emerald-500/10 rounded-lg border border-emerald-500/20">🔍</span>
            <div>
              <p className="text-xs font-bold text-slate-900 dark:text-white">Falcon Eye</p>
              <p className="text-[11px] text-slate-600 dark:text-zinc-400 mt-1 leading-snug">
                Flagged 10+ high-risk non-compliant items accurately.
              </p>
            </div>
          </div>

          <div className="bg-slate-50 dark:bg-zinc-950 p-4 rounded-xl border border-slate-200 dark:border-zinc-800 flex items-start space-x-3.5 hover:border-slate-300 dark:hover:border-zinc-700 transition-colors">
            <span className="text-2xl p-2 bg-cyan-500/10 rounded-lg border border-cyan-500/20">⚡</span>
            <div>
              <p className="text-xs font-bold text-slate-900 dark:text-white">Speedy Auditor</p>
              <p className="text-[11px] text-slate-600 dark:text-zinc-400 mt-1 leading-snug">
                Executed 5 high-throughput scans under 10 minutes.
              </p>
            </div>
          </div>

          <div className="bg-slate-50 dark:bg-zinc-950 p-4 rounded-xl border border-slate-200 dark:border-zinc-800 flex items-start space-x-3.5 hover:border-slate-300 dark:hover:border-zinc-700 transition-colors">
            <span className="text-2xl p-2 bg-amber-500/10 rounded-lg border border-amber-500/20">🛡️</span>
            <div>
              <p className="text-xs font-bold text-slate-900 dark:text-white">Guardian</p>
              <p className="text-[11px] text-slate-600 dark:text-zinc-400 mt-1 leading-snug">
                Maintained over 95% verification accuracy across catalog checks.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}