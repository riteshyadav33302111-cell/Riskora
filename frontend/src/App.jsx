import { useState } from 'react';
import Logo from './components/Logo';
import HomePage from './pages/HomePage';
import ScannerPage from './pages/ScannerPage';
import DashboardPage from './pages/DashboardPage';
import { Home, Search, BarChart2, Github, ExternalLink } from 'lucide-react';

const NAV_ITEMS = [
  { key: 'home',      label: 'Home',      icon: Home },
  { key: 'scanner',   label: 'Scanner',   icon: Search },
  { key: 'dashboard', label: 'Dashboard', icon: BarChart2 },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('home');

  const renderPage = () => {
    switch (activeTab) {
      case 'scanner':   return <ScannerPage />;
      case 'dashboard': return <DashboardPage />;
      default:          return <HomePage />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">

      {/* ── Navbar ── */}
      {activeTab !== 'home' && (
        <header className="sticky top-0 z-50 border-b border-white/10 backdrop-blur-md bg-navy-950/90">
          <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">

            {/* Logo */}
            <button onClick={() => setActiveTab('home')} className="flex-shrink-0">
              <Logo size="sm" />
            </button>

            {/* Nav links */}
            <nav className="flex items-center gap-1">
              {NAV_ITEMS.map(({ key, label, icon: Icon }) => (
                <button
                  key={key}
                  onClick={() => setActiveTab(key)}
                  className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                    activeTab === key
                      ? 'bg-violet-600/20 text-violet-300 border border-violet-500/30'
                      : 'text-slate-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden sm:inline">{label}</span>
                </button>
              ))}
            </nav>

            {/* GitHub link */}
            <a
              href="https://github.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-slate-400 hover:text-white transition-colors text-sm"
            >
              <Github className="w-4 h-4" />
              <span className="hidden sm:inline">Source</span>
              <ExternalLink className="w-3 h-3 opacity-50" />
            </a>
          </div>
        </header>
      )}

      {/* ── Main content ── */}
      <main className={`flex-1 ${activeTab !== 'home' ? 'max-w-6xl mx-auto w-full px-4 py-8' : ''}`}>
        {renderPage()}
      </main>

      {/* ── Bottom nav (mobile, only on inner pages) ── */}
      {activeTab !== 'home' && (
        <nav className="sm:hidden fixed bottom-0 inset-x-0 border-t border-white/10 bg-navy-950/95 backdrop-blur-md z-50">
          <div className="flex">
            {NAV_ITEMS.map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`flex-1 flex flex-col items-center gap-1 py-3 text-xs transition-colors ${
                  activeTab === key ? 'text-violet-400' : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                <Icon className="w-5 h-5" />
                {label}
              </button>
            ))}
          </div>
        </nav>
      )}

      {/* ── Footer ── */}
      <footer className="border-t border-white/5 py-6 text-center text-xs text-slate-600">
        <p>
          Riskora — Intelligent Phishing URL Detection ·{' '}
          Dataset:{' '}
          <a
            href="https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset"
            target="_blank"
            rel="noopener noreferrer"
            className="text-violet-500 hover:text-violet-400 underline"
          >
            PhiUSIIL @ UCI (CC BY 4.0)
          </a>
        </p>
        <p className="mt-1">
          Not a security guarantee — always exercise caution with unknown URLs.
        </p>
      </footer>
    </div>
  );
}
