import React, { useEffect, useState } from 'react';
import { CheckCircle2, Loader2, Cpu, Box, Sparkles } from 'lucide-react';

interface GenerationProgressProps {
  onComplete: () => void;
}

const STAGES = [
  'Understanding requirements & parsing specs',
  'Creating spatial constraints & Shapely plot boundaries',
  'Generating candidate layouts via PyTorch Neural Network',
  'Checking geometry & validating non-overlap constraints',
  'Evaluating designs with Scikit-Learn Quality Model',
  'Optimizing layout Pareto trade-offs',
  'Building 3D house environment & mesh geometries',
  'Placing interior furniture & circulation clearance',
  'Calculating cost intelligence & analytics',
];

export const GenerationProgress: React.FC<GenerationProgressProps> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState<number>(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < STAGES.length - 1) {
          return prev + 1;
        } else {
          clearInterval(interval);
          setTimeout(onComplete, 600);
          return prev;
        }
      });
    }, 450);

    return () => clearInterval(interval);
  }, [onComplete]);

  const progressPercent = Math.round(((currentStep + 1) / STAGES.length) * 100);

  return (
    <div className="max-w-2xl mx-auto my-12 p-8 glass-card rounded-3xl border border-slate-800 shadow-2xl space-y-8 text-center">
      <div className="relative w-24 h-24 mx-auto flex items-center justify-center">
        <div className="absolute inset-0 rounded-full bg-indigo-600/20 blur-xl animate-pulse" />
        <div className="relative w-20 h-20 rounded-2xl bg-dark-800 border border-indigo-500/40 flex items-center justify-center glow-indigo">
          <Cpu className="w-10 h-10 text-indigo-400 animate-bounce" />
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Synthesizing Architectural Concepts</h2>
        <p className="text-xs text-slate-400 mt-1 font-mono">
          Executing local PyTorch DL model, Shapely geometry validation & Pareto optimization
        </p>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs font-mono">
          <span className="text-indigo-400 font-semibold">{STAGES[currentStep]}</span>
          <span className="text-white font-bold">{progressPercent}%</span>
        </div>
        <div className="w-full bg-dark-900 rounded-full h-3 overflow-hidden p-0.5 border border-slate-800">
          <div
            className="bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 h-full rounded-full transition-all duration-300 shadow-sm"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Checklist of Stages */}
      <div className="grid grid-cols-1 gap-2 text-left pt-4 max-h-60 overflow-y-auto pr-2">
        {STAGES.map((stage, idx) => {
          const isDone = idx < currentStep;
          const isCurrent = idx === currentStep;

          return (
            <div
              key={idx}
              className={`p-2.5 rounded-xl border text-xs flex items-center gap-3 transition-all ${
                isDone
                  ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300'
                  : isCurrent
                  ? 'bg-indigo-950/60 border-indigo-500/50 text-white font-semibold shadow-md'
                  : 'bg-dark-900/40 border-slate-800/60 text-slate-500'
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              ) : isCurrent ? (
                <Loader2 className="w-4 h-4 text-indigo-400 animate-spin shrink-0" />
              ) : (
                <div className="w-4 h-4 rounded-full border border-slate-700 shrink-0" />
              )}
              <span>{stage}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
