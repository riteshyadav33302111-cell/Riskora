import { useEffect, useState, useCallback } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import { RefreshCw, TrendingUp, Shield, AlertTriangle, CheckCircle, Cpu } from 'lucide-react';
import { fetchStatistics } from '../utils/api';

const COLORS = {
  phishing:   '#ef4444',
  legitimate: '#10b981',
  purple:     '#8b5cf6',
  cyan:       '#06b6d4',
};

// Custom tooltip for recharts
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-card p-3 border border-white/20 text-sm">
        {label && <p className="text-slate-400 mb-1">{label}</p>}
        {payload.map((entry, i) => (
          <p key={i} className="font-semibold" style={{ color: entry.color || entry.fill }}>
            {entry.name}: {entry.value.toLocaleString()}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// Stat card
function StatCard({ icon: Icon, label, value, color, subtext }) {
  return (
    <div className="glass-card p-5 flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color.bg}`}>
        <Icon className={`w-6 h-6 ${color.text}`} />
      </div>
      <div>
        <p className="text-xs text-slate-400 uppercase tracking-wider">{label}</p>
        <p className={`text-2xl font-bold font-mono ${color.text}`}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>
        {subtext && <p className="text-xs text-slate-500 mt-0.5">{subtext}</p>}
      </div>
    </div>
  );
}

export default function AnalyticsDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchStatistics();
      setStats(data);
      setLastRefresh(new Date());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    // Auto-refresh every 30 seconds
    const interval = setInterval(load, 30_000);
    return () => clearInterval(interval);
  }, [load]);

  if (loading && !stats) {
    return (
      <div className="flex flex-col items-center gap-4 py-16 text-slate-400">
        <RefreshCw className="w-8 h-8 animate-spin" />
        <p>Loading analytics…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-8 text-center border border-red-500/20">
        <AlertTriangle className="w-10 h-10 text-red-400 mx-auto mb-3" />
        <p className="text-red-400 font-semibold mb-1">Failed to load statistics</p>
        <p className="text-slate-500 text-sm mb-4">{error}</p>
        <button
          onClick={load}
          className="px-4 py-2 rounded-lg bg-violet-600/20 border border-violet-500/30 text-violet-400 hover:bg-violet-600/30 transition-colors text-sm"
        >
          Retry
        </button>
      </div>
    );
  }

  const total     = stats?.total_scanned || 0;
  const phishing  = stats?.phishing_count || 0;
  const legit     = stats?.legitimate_count || 0;
  const phishRate = stats ? Math.round((stats.phishing_rate || 0) * 100) : 0;

  const pieData = [
    { name: 'Phishing',   value: phishing || 0 },
    { name: 'Legitimate', value: legit    || 0 },
  ];

  const barData = [
    { name: 'Phishing',   count: phishing },
    { name: 'Legitimate', count: legit },
    { name: 'Total',      count: total },
  ];

  return (
    <div className="space-y-6 animate-fade-in">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="section-heading">Analytics Dashboard</h2>
          <p className="section-subheading">
            Session-level aggregate statistics • Not individual scan history
          </p>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="p-2 rounded-lg border border-white/15 text-slate-400 hover:text-white hover:border-violet-500/40 transition-all"
          title="Refresh statistics"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={TrendingUp}
          label="Total Scanned"
          value={total}
          color={{ text: 'text-cyan-400', bg: 'bg-cyan-500/10' }}
          subtext="this session"
        />
        <StatCard
          icon={AlertTriangle}
          label="Phishing Detected"
          value={phishing}
          color={{ text: 'text-red-400', bg: 'bg-red-500/10' }}
          subtext={total > 0 ? `${phishRate}% of scans` : 'no scans yet'}
        />
        <StatCard
          icon={CheckCircle}
          label="Legitimate URLs"
          value={legit}
          color={{ text: 'text-emerald-400', bg: 'bg-emerald-500/10' }}
          subtext={total > 0 ? `${100 - phishRate}% of scans` : 'no scans yet'}
        />
        <StatCard
          icon={Cpu}
          label="ML Model"
          value={stats?.model_name || '—'}
          color={{ text: 'text-violet-400', bg: 'bg-violet-500/10' }}
          subtext={`${stats?.feature_count || 0} features`}
        />
      </div>

      {total === 0 ? (
        /* No data yet */
        <div className="glass-card p-12 text-center border border-dashed border-white/15">
          <Shield className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400 font-semibold mb-2">No scans yet this session</p>
          <p className="text-slate-600 text-sm">
            Go to the Scanner tab and analyse a URL to see statistics here.
          </p>
        </div>
      ) : (
        /* Charts */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          {/* Pie chart */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">
              Detection Breakdown
            </h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={90}
                  paddingAngle={3}
                  dataKey="value"
                >
                  <Cell fill={COLORS.phishing}   stroke="transparent" />
                  <Cell fill={COLORS.legitimate} stroke="transparent" />
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  iconType="circle"
                  iconSize={8}
                  formatter={(value, entry) => (
                    <span style={{ color: entry.color, fontSize: '12px' }}>{value}</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Bar chart */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">
              URL Count Comparison
            </h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={barData} barCategoryGap="30%">
                <XAxis
                  dataKey="name"
                  tick={{ fill: '#94a3b8', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: '#94a3b8', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  width={35}
                />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {barData.map((entry, i) => (
                    <Cell
                      key={i}
                      fill={
                        i === 0 ? COLORS.phishing :
                        i === 1 ? COLORS.legitimate :
                        COLORS.purple
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Last refreshed */}
      {lastRefresh && (
        <p className="text-xs text-slate-600 text-right">
          Last refreshed: {lastRefresh.toLocaleTimeString()}
        </p>
      )}
    </div>
  );
}
