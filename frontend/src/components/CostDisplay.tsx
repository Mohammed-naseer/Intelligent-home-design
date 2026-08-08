import React from 'react';
import { CostEstimateData } from '../types';
import { DollarSign, AlertTriangle } from 'lucide-react';

interface CostDisplayProps {
  cost: CostEstimateData;
}

export const CostDisplay: React.FC<CostDisplayProps> = ({ cost }) => {
  return (
    <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <DollarSign className="w-4 h-4 text-emerald-400" /> Construction Cost Intelligence
        </h3>
        <div className="text-[11px] bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 px-2.5 py-1 rounded-full font-mono font-medium">
          {cost.budget_tier} Tier
        </div>
      </div>

      {/* Total Cost Hero */}
      <div className="bg-dark-900/80 p-4 rounded-xl border border-slate-800 text-center">
        <div className="text-xs text-slate-400 uppercase tracking-wider font-mono mb-1">Estimated Construction Cost</div>
        <div className="text-3xl font-extrabold text-white font-mono">
          {cost.currency_symbol}{(cost.total_estimated_cost / 100000).toFixed(2)} Lakhs
        </div>
        <div className="text-xs text-slate-400 mt-1">
          {cost.built_up_area_sqft.toFixed(0)} sq ft @ {cost.currency_symbol}{cost.rate_per_sqft.toLocaleString()}/sq ft
        </div>
      </div>

      {/* Itemized Breakdown */}
      <div className="space-y-2">
        {cost.breakdown.map((item, idx) => (
          <div key={idx} className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 flex-1">
              <span className="text-slate-400 w-36 truncate">{item.category}:</span>
              <div className="flex-1 bg-dark-900/80 rounded-full h-1.5 overflow-hidden mx-2">
                <div
                  className="bg-indigo-500 h-full rounded-full"
                  style={{ width: `${item.percentage}%` }}
                />
              </div>
              <span className="text-slate-500 text-[10px] font-mono w-8 text-right">{item.percentage}%</span>
            </div>
            <span className="font-mono font-semibold text-white ml-3 w-24 text-right">
              {cost.currency_symbol}{(item.amount / 100000).toFixed(1)}L
            </span>
          </div>
        ))}
      </div>

      {/* Disclaimer */}
      <div className="flex items-start gap-2 text-[11px] text-amber-200/80 bg-amber-950/30 border border-amber-500/20 p-2.5 rounded-xl">
        <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
        <span>{cost.disclaimer}</span>
      </div>
    </div>
  );
};
