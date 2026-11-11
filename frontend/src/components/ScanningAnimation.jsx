import { Loader2, Radar, Cpu, Shield } from 'lucide-react';

const phases = [
  { key: 'validating', icon: Shield,  label: 'Validating URL format…'   },
  { key: 'scanning',   icon: Radar,   label: 'Extracting URL features…' },
  { key: 'scanning',   icon: Cpu,     label: 'Running ML classifier…'   },
];

export default function ScanningAnimation({ phase }) {
  if (phase === 'idle' || phase === 'done') return null;

  const currentPhase = phases.find((p) => p.key === phase) || phases[0];
  const { icon: Icon, label } = currentPhase;

  return (
    <div className="glass-card p-8 flex flex-col items-center gap-6 animate-fade-in scan-container">
      {/* Pulsing shield */}
      <div className="relative">
        <div className="absolute inset-0 rounded-full bg-violet-500/20 animate-ping" />
        <div className="relative w-16 h-16 rounded-full bg-gradient-to-br from-violet-600/30 to-cyan-600/30 border border-violet-500/40 flex items-center justify-center">
          <Icon className="w-7 h-7 text-violet-400 animate-pulse" />
        </div>
      </div>

      {/* Status text */}
      <div className="text-center space-y-1">
        <p className="text-white font-semibold">{label}</p>
        <p className="text-slate-400 text-sm">This may take a moment</p>
      </div>

      {/* Animated dots */}
      <div className="flex gap-2">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-2 h-2 rounded-full bg-violet-500"
            style={{
              animation: `pulse 1.5s ${i * 0.2}s ease-in-out infinite`,
            }}
          />
        ))}
      </div>

      {/* Progress bar */}
      <div className="w-full h-1 bg-navy-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-violet-500 to-cyan-500 rounded-full"
          style={{
            animation: 'progress 2s ease-in-out infinite',
            width: phase === 'validating' ? '30%' : '75%',
            transition: 'width 0.5s ease-out',
          }}
        />
      </div>

      <style>{`
        @keyframes progress {
          0%   { opacity: 0.6; }
          50%  { opacity: 1; }
          100% { opacity: 0.6; }
        }
      `}</style>
    </div>
  );
}
