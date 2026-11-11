import { Shield, Zap, Brain, Lock, Globe, AlertTriangle } from 'lucide-react';

const features = [
  {
    icon: Brain,
    title: 'ML-Powered Detection',
    description: 'Trained on 235,000+ URLs using Random Forest and Gradient Boosting algorithms.',
    color: 'text-violet-400',
    bg: 'bg-violet-500/10',
    border: 'border-violet-500/20',
  },
  {
    icon: Zap,
    title: 'Instant Analysis',
    description: 'Real-time URL feature extraction and classification in milliseconds.',
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10',
    border: 'border-cyan-500/20',
  },
  {
    icon: Shield,
    title: 'Risk Scoring',
    description: 'Multi-level risk assessment: Low, Medium, and High severity classification.',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/20',
  },
  {
    icon: Lock,
    title: 'Privacy First',
    description: 'Your URLs are never fetched or stored. Analysis is purely structural.',
    color: 'text-amber-400',
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/20',
  },
  {
    icon: Globe,
    title: 'Explainable Results',
    description: 'Transparent breakdown of suspicious indicators found in each URL.',
    color: 'text-pink-400',
    bg: 'bg-pink-500/10',
    border: 'border-pink-500/20',
  },
  {
    icon: AlertTriangle,
    title: 'No Blind Trust',
    description: 'Every prediction includes a disclaimer — always exercise your own judgment.',
    color: 'text-orange-400',
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/20',
  },
];

export default function FeatureGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {features.map(({ icon: Icon, title, description, color, bg, border }) => (
        <div
          key={title}
          className={`glass-card p-5 border ${border} hover:scale-[1.02] transition-transform duration-200`}
        >
          <div className={`inline-flex p-2.5 rounded-lg ${bg} mb-3`}>
            <Icon className={`w-5 h-5 ${color}`} />
          </div>
          <h3 className="font-semibold text-white mb-1.5">{title}</h3>
          <p className="text-slate-400 text-sm leading-relaxed">{description}</p>
        </div>
      ))}
    </div>
  );
}
