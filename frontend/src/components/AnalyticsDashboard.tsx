import React, { useEffect, useState } from 'react';
import { AnalyticsData, ModelHistoryItem } from '../types';
import {
  BarChart3,
  TrendingUp,
  Cpu,
  RefreshCw,
  CheckCircle2,
  DollarSign,
  PieChart as PieIcon,
  Layers,
  Award,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
} from 'recharts';

export const AnalyticsDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [retraining, setRetraining] = useState<boolean>(false);

  const fetchAnalytics = async () => {
    try {
      const res = await fetch('/api/v2/analytics');
      const data = await res.json();
      if (data.status === 'success') {
        setAnalytics(data.analytics);
      }
    } catch (e) {
      console.error('Analytics fetch error:', e);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const handleRetrain = async () => {
    setRetraining(true);
    try {
      const res = await fetch('/api/v2/trigger-retrain', { method: 'POST' });
      const data = await res.json();
      if (data.status === 'success') {
        await fetchAnalytics();
      }
    } catch (e) {
      console.error('Retrain error:', e);
    } finally {
      setRetraining(false);
    }
  };

  if (!analytics) {
    return <div className="text-center py-12 text-slate-400 text-xs">Loading telemetry analytics...</div>;
  }

  // Chart dataset mock mappings
  const spaceUtilData = [
    { range: '70-80%', count: 12 },
    { range: '80-88%', count: 42 },
    { range: '88-94%', count: 86 },
    { range: '94-98%', count: 34 },
  ];

  const modelVersionData = analytics.model_history.map((v: ModelHistoryItem) => ({
    version: v.version,
    accuracy: v.accuracy,
    validity: v.validity_rate,
  }));

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-indigo-400" /> Platform Telemetry & ML Model Analytics
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Tracks total layout generations, user selection rates, spatial efficiency metrics, and model version progression.
          </p>
        </div>

        <button
          disabled={retraining}
          onClick={handleRetrain}
          className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg flex items-center gap-2 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${retraining ? 'animate-spin' : ''}`} />
          {retraining ? 'Retraining ML Models...' : 'Trigger Model Retraining'}
        </button>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-4 rounded-2xl border border-slate-800">
          <div className="text-xs text-slate-400">Total Designs Generated</div>
          <div className="text-2xl font-extrabold text-white font-mono mt-1">
            {analytics.total_generated_designs}
          </div>
          <div className="text-[11px] text-emerald-400 mt-1 font-medium">
            {analytics.accepted_designs} Accepted ({Math.round((analytics.accepted_designs / analytics.total_generated_designs) * 100)}%)
          </div>
        </div>

        <div className="glass-card p-4 rounded-2xl border border-slate-800">
          <div className="text-xs text-slate-400">Avg Space Utilization</div>
          <div className="text-2xl font-extrabold text-indigo-400 font-mono mt-1">
            {analytics.avg_space_utilization}%
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            Across all plot sizes
          </div>
        </div>

        <div className="glass-card p-4 rounded-2xl border border-slate-800">
          <div className="text-xs text-slate-400">Avg Overall Design Score</div>
          <div className="text-2xl font-extrabold text-emerald-400 font-mono mt-1">
            {analytics.avg_design_score}%
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            Evaluated by Quality Predictor
          </div>
        </div>

        <div className="glass-card p-4 rounded-2xl border border-slate-800">
          <div className="text-xs text-slate-400">Active Model Version</div>
          <div className="text-2xl font-extrabold text-purple-400 font-mono mt-1">
            {analytics.active_model_version}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            {analytics.feedback_count} feedback entries logged
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Model Accuracy over Versions */}
        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Cpu className="w-4 h-4 text-indigo-400" /> Model Accuracy & Validity Progression
          </h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={modelVersionData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="version" stroke="#94A3B8" fontSize={11} />
                <YAxis stroke="#94A3B8" fontSize={11} domain={[80, 100]} />
                <Tooltip contentStyle={{ background: '#0B0F19', borderColor: '#374151', borderRadius: '8px', fontSize: '11px' }} />
                <Line type="monotone" dataKey="accuracy" name="Accuracy %" stroke="#818CF8" strokeWidth={3} />
                <Line type="monotone" dataKey="validity" name="Validity %" stroke="#34D399" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Space Utilization Distribution */}
        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-400" /> Space Utilization Efficiency Distribution
          </h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={spaceUtilData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="range" stroke="#94A3B8" fontSize={11} />
                <YAxis stroke="#94A3B8" fontSize={11} />
                <Tooltip contentStyle={{ background: '#0B0F19', borderColor: '#374151', borderRadius: '8px', fontSize: '11px' }} />
                <Bar dataKey="count" fill="#6366F1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
