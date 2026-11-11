import Logo from '../components/Logo';
import UrlInput from '../components/UrlInput';
import ScanningAnimation from '../components/ScanningAnimation';
import ScanResult from '../components/ScanResult';
import FeatureGrid from '../components/FeatureGrid';
import { useUrlScanner } from '../hooks/useUrlScanner';
import { ArrowDown } from 'lucide-react';

// Sample URLs shown as quick-scan suggestions
const EXAMPLE_URLS = [
  'https://www.google.com',
  'https://github.com/openai/openai-python',
  'http://paypal-verify.tk/account?token=abc123',
];

export default function HomePage({ onScanComplete }) {
  const { url, setUrl, result, isLoading, error, scanPhase, scan, reset } = useUrlScanner();

  const handleScan = async (inputUrl) => {
    await scan(inputUrl);
  };

  // If we have a result, hand off to scanner view
  if (result) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-10">
        <div className="mb-8 flex items-center justify-between">
          <Logo />
        </div>
        <ScanResult result={result} onNewScan={reset} />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">

      {/* ── Hero ── */}
      <section className="flex-1 flex flex-col items-center justify-center px-4 py-20 text-center">
        {/* Top badge */}
        <div className="mb-8 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/25 text-violet-400 text-xs font-semibold uppercase tracking-wider">
          <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
          ML-Powered Threat Detection
        </div>

        {/* Logo */}
        <div className="mb-6">
          <Logo size="lg" />
        </div>

        {/* Tagline */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white leading-tight mb-4 max-w-3xl">
          Know Before You{' '}
          <span className="text-gradient-purple-cyan">Click</span>
        </h1>

        <p className="text-slate-400 text-lg mb-10 max-w-xl leading-relaxed">
          Riskora analyses URLs in real time using machine learning to detect phishing
          attempts, assess risk levels, and explain suspicious indicators.
        </p>

        {/* URL Scanner */}
        <div className="w-full max-w-2xl mb-6">
          {scanPhase === 'idle' || scanPhase === 'done' ? (
            <UrlInput
              url={url}
              setUrl={setUrl}
              onScan={handleScan}
              isLoading={isLoading}
              error={error}
            />
          ) : (
            <ScanningAnimation phase={scanPhase} />
          )}
        </div>

        {/* Example URLs */}
        <div className="flex flex-wrap gap-2 justify-center">
          <span className="text-xs text-slate-500 mr-1 mt-1.5">Try:</span>
          {EXAMPLE_URLS.map((u) => (
            <button
              key={u}
              onClick={() => { setUrl(u); handleScan(u); }}
              className="text-xs font-mono text-slate-400 hover:text-cyan-400 px-2.5 py-1 rounded-lg border border-white/10 hover:border-cyan-500/30 transition-all duration-150 max-w-[220px] truncate"
              title={u}
            >
              {u.length > 40 ? u.slice(0, 38) + '…' : u}
            </button>
          ))}
        </div>

        {/* Scroll hint */}
        <div className="mt-16 flex flex-col items-center gap-2 text-slate-600 animate-bounce">
          <span className="text-xs">Explore features</span>
          <ArrowDown className="w-4 h-4" />
        </div>
      </section>

      {/* ── Feature Grid ── */}
      <section className="px-4 pb-20 max-w-5xl mx-auto w-full">
        <div className="text-center mb-10">
          <h2 className="text-2xl font-bold text-white mb-2">Why Riskora?</h2>
          <p className="text-slate-400">
            Transparent, explainable ML — not a black box.
          </p>
        </div>
        <FeatureGrid />
      </section>
    </div>
  );
}
