import {
  CheckCircle, XCircle, AlertTriangle, Info,
  ChevronDown, ChevronUp, Shield, Cpu, ExternalLink
} from 'lucide-react';
import { useState } from 'react';

// ── Utility helpers ──────────────────────────────────────────────────────────

function getRiskColor(riskLevel) {
  switch (riskLevel) {
    case 'high':   return { text: 'text-red-400',     bg: 'bg-red-500/15',     border: 'border-red-500/30',    glow: 'shadow-red-500/20'    };
    case 'medium': return { text: 'text-amber-400',   bg: 'bg-amber-500/15',   border: 'border-amber-500/30',  glow: 'shadow-amber-500/20'  };
    default:       return { text: 'text-emerald-400', bg: 'bg-emerald-500/15', border: 'border-emerald-500/30',glow: 'shadow-emerald-500/20' };
  }
}

function getSeverityIcon(severity) {
  switch (severity) {
    case 'high':   return <XCircle     className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />;
    case 'medium': return <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />;
    default:       return <Info         className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />;
  }
}

// ── Confidence Meter ─────────────────────────────────────────────────────────

function ConfidenceMeter({ phishingProbability, legitimateProbability }) {
  const phishPct = Math.round(phishingProbability * 100);
  const legitPct = Math.round(legitimateProbability * 100);

  return (
    <div className="space-y-2">
      <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Model Probabilities</p>

      <div className="space-y-1.5">
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400 w-20">Phishing</span>
          <div className="flex-1 h-2 bg-navy-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-red-500 to-orange-500 rounded-full transition-all duration-700 ease-out"
              style={{ width: `${phishPct}%` }}
            />
          </div>
          <span className="text-xs font-mono font-bold text-red-400 w-10 text-right">
            {phishPct}%
          </span>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400 w-20">Legitimate</span>
          <div className="flex-1 h-2 bg-navy-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-full transition-all duration-700 ease-out"
              style={{ width: `${legitPct}%` }}
            />
          </div>
          <span className="text-xs font-mono font-bold text-emerald-400 w-10 text-right">
            {legitPct}%
          </span>
        </div>
      </div>
    </div>
  );
}

// ── Feature Details Accordion ────────────────────────────────────────────────

function FeatureAccordion({ features }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="border border-white/10 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-white/5 transition-colors"
      >
        <span className="text-sm font-semibold text-slate-300 flex items-center gap-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          Extracted Features ({features.length})
        </span>
        {open ? (
          <ChevronUp className="w-4 h-4 text-slate-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-slate-400" />
        )}
      </button>

      {open && (
        <div className="border-t border-white/10 p-4 max-h-80 overflow-y-auto">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {features.map(({ name, value }) => (
              <div key={name} className="flex items-center justify-between gap-2 py-1 border-b border-white/5">
                <span className="text-xs text-slate-400 font-mono truncate">{name}</span>
                <span className="text-xs font-mono font-bold text-cyan-400 ml-2 flex-shrink-0">
                  {typeof value === 'number' && !Number.isInteger(value)
                    ? value.toFixed(4)
                    : String(value)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Main Result Card ─────────────────────────────────────────────────────────

export default function ScanResult({ result, onNewScan }) {
  if (!result) return null;

  const isPhishing = result.prediction === 'phishing';
  const riskColors = getRiskColor(result.risk_level);

  return (
    <div className="space-y-4 animate-slide-up">

      {/* ── Header verdict ── */}
      <div
        className={`glass-card p-6 border ${riskColors.border} shadow-lg ${riskColors.glow}`}
      >
        <div className="flex flex-col sm:flex-row sm:items-start gap-4">

          {/* Icon */}
          <div className={`flex-shrink-0 w-14 h-14 rounded-2xl ${riskColors.bg} flex items-center justify-center`}>
            {isPhishing ? (
              <XCircle className={`w-7 h-7 ${riskColors.text}`} />
            ) : (
              <CheckCircle className={`w-7 h-7 ${riskColors.text}`} />
            )}
          </div>

          {/* Verdict text */}
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <h2 className={`text-2xl font-bold ${riskColors.text} uppercase tracking-wide`}>
                {isPhishing ? 'Phishing Detected' : 'Looks Legitimate'}
              </h2>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase border ${riskColors.bg} ${riskColors.text} ${riskColors.border}`}>
                {result.risk_level} risk
              </span>
            </div>

            {/* URL truncated */}
            <p className="text-slate-400 text-sm font-mono truncate" title={result.url}>
              {result.url}
            </p>
          </div>

          {/* Confidence */}
          <div className="flex-shrink-0 text-right">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Confidence</p>
            <p className={`text-3xl font-bold font-mono ${riskColors.text}`}>
              {Math.round(result.confidence * 100)}%
            </p>
            <p className="text-xs text-slate-500 mt-0.5">{result.model_name}</p>
          </div>
        </div>
      </div>

      {/* ── Probabilities ── */}
      <div className="glass-card p-5">
        <ConfidenceMeter
          phishingProbability={result.phishing_probability}
          legitimateProbability={result.legitimate_probability}
        />
      </div>

      {/* ── Suspicious Indicators ── */}
      {result.suspicious_indicators.length > 0 && (
        <div className="glass-card p-5 space-y-3">
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Shield className="w-4 h-4 text-amber-400" />
            Suspicious Indicators ({result.suspicious_indicators.length})
          </h3>

          <div className="space-y-3">
            {result.suspicious_indicators.map((ind, idx) => (
              <div key={idx} className="flex gap-3">
                {getSeverityIcon(ind.severity)}
                <div>
                  <p className="text-sm font-medium text-white">{ind.indicator}</p>
                  <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">{ind.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── No indicators (legitimate) ── */}
      {result.suspicious_indicators.length === 0 && !isPhishing && (
        <div className="glass-card p-5 flex items-center gap-3 border border-emerald-500/20">
          <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          <p className="text-sm text-slate-300">
            No suspicious indicators detected in this URL.
          </p>
        </div>
      )}

      {/* ── Feature accordion ── */}
      <FeatureAccordion features={result.features} />

      {/* ── Disclaimer ── */}
      <div className="flex gap-2.5 p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
        <Info className="w-4 h-4 text-slate-400 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-slate-400 leading-relaxed">{result.disclaimer}</p>
      </div>

      {/* ── Scan another ── */}
      <button
        onClick={onNewScan}
        className="w-full py-3 rounded-xl border border-white/15 text-slate-300 hover:border-violet-500/50 hover:text-white hover:bg-violet-500/10 transition-all duration-200 font-medium text-sm"
      >
        ← Scan Another URL
      </button>
    </div>
  );
}
