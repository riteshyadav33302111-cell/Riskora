import { Shield } from 'lucide-react';

export default function Logo({ size = 'md' }) {
  const sizes = {
    sm: { icon: 'w-6 h-6', text: 'text-lg', sub: 'text-xs' },
    md: { icon: 'w-8 h-8', text: 'text-2xl', sub: 'text-xs' },
    lg: { icon: 'w-12 h-12', text: 'text-4xl', sub: 'text-sm' },
  };
  const s = sizes[size] || sizes.md;

  return (
    <div className="flex items-center gap-2.5">
      {/* Shield icon with gradient */}
      <div className="relative flex-shrink-0">
        <div className={`${s.icon} rounded-xl bg-gradient-to-br from-violet-600 to-cyan-600 flex items-center justify-center shadow-lg shadow-violet-500/30`}>
          <Shield className="w-4 h-4 text-white" strokeWidth={2.5} />
        </div>
        {/* Glow dot */}
        <div className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-cyan-400 shadow-sm shadow-cyan-400/70" />
      </div>

      {/* Wordmark */}
      <div>
        <span className={`${s.text} font-bold tracking-tight text-gradient-purple-cyan`}>
          Riskora
        </span>
        {size === 'lg' && (
          <p className={`${s.sub} text-slate-400 mt-0.5`}>
            Intelligent Phishing URL Detection
          </p>
        )}
      </div>
    </div>
  );
}
