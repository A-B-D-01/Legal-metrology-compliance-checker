"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { label: 'Overview', path: '/dashboard' },
    { label: 'Audit Engine', path: '/check-compliance' },
    { label: 'Product Catalog', path: '/products' },
    { label: 'Seller Risk', path: '/seller-verification' },
    { label: 'Legal Advisor AI', path: '/chatbot' },
    { label: 'Rewards', path: '/rewards' },
  ];

  return (
    <nav className="bg-zinc-950/80 backdrop-blur-xl border-b border-zinc-800/80 sticky top-0 z-50 shadow-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link href="/" className="flex items-center space-x-2 group">
              <span className="text-xl font-black tracking-wider bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent group-hover:opacity-95 transition-opacity">
                LEGALGUARD
              </span>
            </Link>
            
            <div className="hidden md:flex space-x-2">
              {navItems.map((item) => {
                const isActive = pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    href={item.path}
                    className={`px-3.5 py-2 rounded-lg text-xs font-semibold tracking-wide transition-all duration-200 ${
                      isActive
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 shadow-[0_0_20px_rgba(16,185,129,0.12)]'
                        : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60'
                    }`}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Link
              href="/auth/login"
              className="px-4 py-2 text-xs font-semibold uppercase tracking-wider text-zinc-300 hover:text-white transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/auth/signup"
              className="px-4 py-2 text-xs font-semibold uppercase tracking-wider bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-zinc-950 rounded-lg shadow-lg shadow-emerald-950/50 transition-all transform active:scale-95"
            >
              Get Started
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}