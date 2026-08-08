import React, { useState } from 'react';
import { CandidateDesign } from '../types';
import { FloorPlan2D } from './FloorPlan2D';
import { Box, CheckCircle2, Maximize2, Star } from 'lucide-react';

interface DesignComparisonProps {
  designs:        CandidateDesign[];
  onSelectDesign: (d: CandidateDesign) => void;
  onOpen3D:       (d: CandidateDesign) => void;
}

const SCORE_LABELS: Array<{ key: keyof CandidateDesign['quality_scores']; label: string; color: string }> = [
  { key: 'space_efficiency', label: 'Space',      color: '#6366f1' },
  { key: 'natural_light',    label: 'Light',      color: '#f59e0b' },
  { key: 'privacy_score',    label: 'Privacy',    color: '#10b981' },
  { key: 'circulation_flow', label: 'Flow',       color: '#06b6d4' },
  { key: 'vastu_score',      label: 'Cultural',   color: '#8b5cf6' },
  { key: 'overall_score',    label: 'Overall',    color: '#ec4899' },
];

export const DesignComparison: React.FC<DesignComparisonProps> = ({
  designs, onSelectDesign, onOpen3D,
}) => {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h2 style={{ fontSize: 22, fontWeight: 800, color: '#f8fafc', marginBottom: 4 }}>
          Layout Comparison
        </h2>
        <p style={{ fontSize: 13, color: '#94a3b8' }}>
          {designs.length} AI-generated candidates ranked by Pareto optimization. Click a design to view in 3D.
        </p>
      </div>

      {/* Comparison Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 20 }}>
        {designs.map((design) => {
          const qs = design.quality_scores;
          const isHovered = hoveredId === design.design_id;
          const isBest = design.pareto_rank === 1;

          return (
            <div
              key={design.design_id}
              onMouseEnter={() => setHoveredId(design.design_id)}
              onMouseLeave={() => setHoveredId(null)}
              className="glass-card fade-in-up"
              style={{
                borderRadius: 20, overflow: 'hidden', cursor: 'pointer',
                border: isBest ? '1px solid rgba(99,102,241,0.5)' : '1px solid var(--color-border)',
                boxShadow: isHovered ? 'var(--shadow-glow)' : 'var(--shadow-md)',
                transform: isHovered ? 'translateY(-4px)' : 'none',
                transition: 'all 0.25s cubic-bezier(0.4,0,0.2,1)',
                position: 'relative',
              }}
            >
              {isBest && (
                <div style={{
                  position: 'absolute', top: 12, right: 12, zIndex: 10,
                  background: 'rgba(99,102,241,0.2)', border: '1px solid rgba(99,102,241,0.4)',
                  borderRadius: 99, padding: '3px 10px', display: 'flex', alignItems: 'center', gap: 5,
                  fontSize: 11, fontWeight: 700, color: '#a5b4fc',
                }}>
                  <Star size={11} fill="#a5b4fc" /> Best Design
                </div>
              )}

              {/* Floor plan 2D canvas */}
              <div style={{ background: 'rgba(7,11,20,0.8)', padding: 4 }}>
                <FloorPlan2D design={design} activeFloor={0} width={320} height={220} />
              </div>

              {/* Content */}
              <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontSize: 15, fontWeight: 700, color: '#f8fafc' }}>
                      Design Concept #{design.candidate_index + 1}
                    </div>
                    <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2, textTransform: 'capitalize' }}>
                      {design.architectural_style} · Rank #{design.pareto_rank} · {design.total_built_up_area.toFixed(0)} sqft
                    </div>
                  </div>
                  <div style={{
                    background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.3)',
                    borderRadius: 8, padding: '4px 10px', fontFamily: 'monospace', fontWeight: 800,
                    fontSize: 18, color: '#a5b4fc',
                  }}>
                    {(qs.overall_score * 100).toFixed(0)}%
                  </div>
                </div>

                {/* Score Bars */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {SCORE_LABELS.map(({ key, label, color }) => (
                    <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ width: 52, fontSize: 10, color: '#94a3b8', fontWeight: 600, flexShrink: 0 }}>{label}</span>
                      <div style={{ flex: 1, height: 5, background: 'rgba(255,255,255,0.06)', borderRadius: 99 }}>
                        <div style={{ width: `${qs[key] * 100}%`, height: '100%', background: color, borderRadius: 99, transition: 'width 0.5s' }} />
                      </div>
                      <span style={{ width: 32, fontSize: 10, color: '#f8fafc', fontFamily: 'monospace', fontWeight: 700, textAlign: 'right' }}>
                        {(qs[key] * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>

                {/* Constraint badge */}
                <div style={{ display: 'flex', gap: 8 }}>
                  <div style={{
                    flex: 1, display: 'flex', alignItems: 'center', gap: 5, fontSize: 11,
                    background: design.constraint_satisfied ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                    border: `1px solid ${design.constraint_satisfied ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`,
                    borderRadius: 8, padding: '5px 10px',
                    color: design.constraint_satisfied ? '#6ee7b7' : '#fca5a5',
                    fontWeight: 600,
                  }}>
                    <CheckCircle2 size={12} />
                    {design.constraint_satisfied ? 'All Constraints Met' : 'Minor Violations'}
                  </div>
                  {design.cost_estimate && (
                    <div style={{
                      fontSize: 11, background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)',
                      borderRadius: 8, padding: '5px 10px', color: '#34d399', fontFamily: 'monospace', fontWeight: 700,
                    }}>
                      {design.cost_estimate.currency_symbol}
                      {(design.cost_estimate.total_estimated_cost / 100000).toFixed(1)}L
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    className="btn btn-primary"
                    style={{ flex: 1, fontSize: 12 }}
                    onClick={() => onSelectDesign(design)}
                  >
                    <CheckCircle2 size={13} /> Select Design
                  </button>
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={() => onOpen3D(design)}
                    title="View in 3D"
                  >
                    <Box size={14} />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
