"use client";

import { useState } from 'react';
import Link from 'next/link';

export default function SignupPage() {
  const [formData, setFormData] = useState({ email: '', password: '', role: 'auditor' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed');
      }

      window.location.href = '/auth/login';
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-16 p-8 bg-zinc-900/90 backdrop-blur-2xl rounded-2xl border border-zinc-800 shadow-[0_0_50px_rgba(0,0,0,0.8)] relative">
      <div className="absolute -top-px left-1/2 -translate-x-1/2 w-32 h-[2px] bg-gradient-to-r from-transparent via-cyan-500 to-transparent" />

      <h2 className="text-2xl font-bold tracking-tight text-white mb-1">Join LegalGuard</h2>
      <p className="text-zinc-400 text-xs tracking-wide uppercase mb-6">Automate legal audits & compliance pipelines</p>

      {error && (
        <div className="mb-6 p-3.5 bg-red-950/60 border border-red-500/50 text-red-200 text-xs rounded-xl shadow-lg">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold tracking-wider uppercase text-zinc-400 mb-1.5">Work Email</label>
          <input
            type="email"
            required
            className="w-full px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all text-sm"
            placeholder="auditor@legalguard.ai"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-xs font-semibold tracking-wider uppercase text-zinc-400 mb-1.5">Create Password</label>
          <input
            type="password"
            required
            className="w-full px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl text-white placeholder-zinc-600 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all text-sm"
            placeholder="••••••••"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 mt-2 bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 text-zinc-950 font-bold uppercase tracking-wider text-xs rounded-xl shadow-lg shadow-cyan-950/50 transition-all transform active:scale-[0.98] disabled:opacity-50"
        >
          {loading ? 'Initializing Workspace...' : 'Register Workspace'}
        </button>
      </form>

      <p className="mt-8 text-center text-xs text-zinc-400">
        Already registered?{' '}
        <Link href="/auth/login" className="text-cyan-400 font-semibold hover:underline">
          Sign in here
        </Link>
      </p>
    </div>
  );
}