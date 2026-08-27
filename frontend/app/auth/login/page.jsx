"use client";

import { useState } from 'react';
import Link from 'next/link';

export default function LoginPage() {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }

      localStorage.setItem('access_token', data.access_token);
      window.location.href = '/dashboard';
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-16 p-8 bg-white dark:bg-zinc-900/90 backdrop-blur-2xl rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-xl dark:shadow-[0_0_50px_rgba(0,0,0,0.8)] relative">
      <div className="absolute -top-px left-1/2 -translate-x-1/2 w-32 h-[2px] bg-gradient-to-r from-transparent via-emerald-500 to-transparent" />
      
      <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white mb-1">Welcome Back</h2>
      <p className="text-slate-600 dark:text-zinc-400 text-xs tracking-wide uppercase mb-6">Sign in to your regulatory intelligence portal</p>

      {error && (
        <div className="mb-6 p-3.5 bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-500/50 text-red-700 dark:text-red-200 text-xs rounded-xl shadow-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold tracking-wider uppercase text-slate-600 dark:text-zinc-400 mb-1.5">Work Email</label>
          <input
            type="email"
            required
            className="w-full px-4 py-3 bg-slate-100 dark:bg-zinc-950 border border-slate-300 dark:border-zinc-800 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-600 focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all text-sm"
            placeholder="auditor@legalguard.ai"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-xs font-semibold tracking-wider uppercase text-slate-600 dark:text-zinc-400 mb-1.5">Password</label>
          <input
            type="password"
            required
            className="w-full px-4 py-3 bg-slate-100 dark:bg-zinc-950 border border-slate-300 dark:border-zinc-800 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-600 focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all text-sm"
            placeholder="••••••••"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 mt-2 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white dark:text-zinc-950 font-bold uppercase tracking-wider text-xs rounded-xl shadow-md transition-all transform active:scale-[0.98] disabled:opacity-50"
        >
          {loading ? 'Authenticating Access...' : 'Authenticate'}
        </button>
      </form>

      <p className="mt-8 text-center text-xs text-slate-600 dark:text-zinc-400">
        New to LegalGuard?{' '}
        <Link href="/auth/signup" className="text-emerald-600 dark:text-emerald-400 font-semibold hover:underline">
          Create an organization workspace
        </Link>
      </p>
    </div>
  );
}