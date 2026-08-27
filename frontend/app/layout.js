import './globals.css';
import Navbar from './Navbar';
import { Providers } from './providers';

export const metadata = {
  title: 'LegalGuard - AI-Driven Legal & E-Commerce Compliance Engine',
  description: 'Automated legal verification, OCR product label auditing, and RAG-powered regulatory monitoring.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-slate-50 text-zinc-900 dark:bg-[#060709] dark:text-zinc-100 min-h-screen flex flex-col font-sans antialiased selection:bg-emerald-500 selection:text-black relative overflow-x-hidden transition-colors duration-300">
        <Providers>
          {/* Ambient background glow effects (visible in dark mode) */}
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

          {/* Sticky Navigation Header */}
          <Navbar />

          {/* Main Content Viewport */}
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
            {children}
          </main>

          {/* Global Minimal Footer */}
          <footer className="border-t border-zinc-200 dark:border-zinc-900/80 py-6 text-center text-xs text-zinc-500 relative z-10 transition-colors">
            <p>© {new Date().getFullYear()} LegalGuard. Automated Legal Auditing & Regulatory Risk Management.</p>
          </footer>
        </Providers>
      </body>
    </html>
  );
}