import React from 'react';
import { AlertTriangle } from 'lucide-react';

export const SafetyDisclaimer: React.FC = () => {
  return (
    <div className="bg-amber-950/30 border border-amber-500/30 p-3 rounded-xl text-xs text-amber-200/90 flex items-start gap-2.5 shadow-sm">
      <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
      <div>
        <span className="font-semibold text-amber-300">Conceptual Limitation Disclaimer: </span>
        AI House Architect generates conceptual residential designs and visualizations. It is not a substitute for licensed architectural, structural, electrical, plumbing, or regulatory engineering review.
      </div>
    </div>
  );
};
