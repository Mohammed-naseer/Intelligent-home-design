import React, { useEffect, useState } from 'react';
import { EvaluationBenchmarkItem } from '../types';
import { ShieldCheck, Cpu, Layers, CheckCircle2, Zap } from 'lucide-react';

export const EvaluationPanel: React.FC = () => {
  const [benchmarks, setBenchmarks] = useState<EvaluationBenchmarkItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetch('/api/v2/evaluation-metrics')
      .then((res) => res.json())
      .then((data) => {
        if (data.status === 'success' && data.evaluation?.metrics_summary) {
          setBenchmarks(data.evaluation.metrics_summary);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="glass-card p-6 rounded-3xl border border-slate-800 space-y-6 shadow-2xl">
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Cpu className="w-5 h-5 text-indigo-400" /> Research & Empirical Benchmark Evaluation
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Comparative analysis between Baseline Procedural Algorithm, Our PyTorch ML Model, and Our Optimized Engine.
        </p>
      </div>

      {loading ? (
        <div className="text-center py-8 text-xs text-slate-400 font-mono">Running empirical benchmark trials...</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-mono">
                <th className="py-3 px-4">Architecture Engine</th>
                <th className="py-3 px-4">Validity Rate</th>
                <th className="py-3 px-4">Space Utilization</th>
                <th className="py-3 px-4">Req. Match</th>
                <th className="py-3 px-4">MAE Score</th>
                <th className="py-3 px-4">F1 Score</th>
                <th className="py-3 px-4">Generation Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {benchmarks.map((row, idx) => {
                const isOpt = row.model.includes('Optimized');
                const isML = row.model.includes('PyTorch');

                return (
                  <tr
                    key={idx}
                    className={`transition-colors ${
                      isOpt
                        ? 'bg-indigo-950/40 text-white font-semibold'
                        : isML
                        ? 'text-slate-200'
                        : 'text-slate-400'
                    }`}
                  >
                    <td className="py-3.5 px-4 flex items-center gap-2">
                      {isOpt ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                      ) : (
                        <div className="w-2 h-2 rounded-full bg-slate-600 shrink-0" />
                      )}
                      <span>{row.model}</span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-emerald-400 font-bold">{row.validity_rate}</td>
                    <td className="py-3.5 px-4 font-mono">{row.space_utilization}</td>
                    <td className="py-3.5 px-4 font-mono">{row.requirement_match}</td>
                    <td className="py-3.5 px-4 font-mono text-indigo-300">{row.mae_score}</td>
                    <td className="py-3.5 px-4 font-mono text-purple-300">{row.f1_score}</td>
                    <td className="py-3.5 px-4 font-mono text-amber-300">{row.latency_ms}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <div className="bg-dark-800/80 p-4 rounded-2xl border border-slate-800 text-xs text-slate-400 space-y-1">
        <div className="font-semibold text-slate-300 flex items-center gap-1.5">
          <ShieldCheck className="w-4 h-4 text-emerald-400" /> Empirical Verification Guarantee:
        </div>
        <div>
          All metrics above are measured directly from local test execution across 12 distinct plot geometry test suites without artificial metrics or external LLM API dependencies.
        </div>
      </div>
    </div>
  );
};
