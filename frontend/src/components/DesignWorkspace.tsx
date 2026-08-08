import React, { useState } from 'react';
import { DesignRequirement, CandidateDesign, RoomSpec } from '../types';
import { HouseViewer3D } from './HouseViewer3D';
import { DesignComparison } from './DesignComparison';
import { WhatIfStudio } from './WhatIfStudio';
import { AnalyticsDashboard } from './AnalyticsDashboard';
import { EvaluationPanel } from './EvaluationPanel';
import { SafetyDisclaimer } from './SafetyDisclaimer';
import { CostDisplay } from './CostDisplay';
import {
  Sliders, Box, BarChart3, Cpu, Layers, DollarSign,
  Compass, Building2, Layout, RefreshCcw, CheckCircle2,
} from 'lucide-react';

type ViewTab = '3d' | 'comparison' | 'whatif' | 'analytics' | 'evaluation';

interface DesignWorkspaceProps {
  initialRequirements:     DesignRequirement;
  initialCandidateDesigns: CandidateDesign[];
  onResetRequirements:     () => void;
}

const ScoreRow: React.FC<{ label: string; value: number; color?: string }> = ({
  label, value, color = '#6366f1',
}) => (
  <div className="space-y-1">
    <div className="flex justify-between text-xs">
      <span style={{ color: '#94a3b8' }}>{label}</span>
      <span className="font-mono font-bold text-white">{(value * 100).toFixed(0)}%</span>
    </div>
    <div className="score-bar-track">
      <div className="score-bar-fill" style={{ width: `${value * 100}%`, background: color }} />
    </div>
  </div>
);

export const DesignWorkspace: React.FC<DesignWorkspaceProps> = ({
  initialRequirements,
  initialCandidateDesigns,
  onResetRequirements,
}) => {
  const [activeTab, setActiveTab]       = useState<ViewTab>('3d');
  const [requirements]                  = useState<DesignRequirement>(initialRequirements);
  const [designs, setDesigns]           = useState<CandidateDesign[]>(initialCandidateDesigns);
  const [selectedDesign, setSelectedDesign] = useState<CandidateDesign>(initialCandidateDesigns[0]);
  const [, setFocusedRoom]              = useState<RoomSpec | null>(null);

  const handleApplyRedesign = (newDesigns: CandidateDesign[]) => {
    setDesigns(newDesigns);
    setSelectedDesign(newDesigns[0]);
  };

  const navItems: Array<{ id: ViewTab; label: string; Icon: React.FC<{ className?: string }> }> = [
    { id: '3d',         label: '3D Visualization',    Icon: Box },
    { id: 'comparison', label: 'Layout Comparison',   Icon: Layout },
    { id: 'whatif',     label: 'What-If Redesign',    Icon: Sliders },
    { id: 'analytics',  label: 'Analytics',           Icon: BarChart3 },
    { id: 'evaluation', label: 'ML Evaluation',       Icon: Cpu },
  ];

  const qs = selectedDesign.quality_scores;

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg-deepest)', color: 'var(--color-text-primary)', display: 'flex', flexDirection: 'column' }}>

      {/* Top Bar */}
      <header style={{ background: 'rgba(7,11,20,0.95)', backdropFilter: 'blur(20px)', borderBottom: '1px solid var(--color-border)', padding: '12px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'sticky', top: 0, zIndex: 40 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: 'var(--gradient-brand)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: 'var(--shadow-glow-sm)' }}>
            <Box size={20} color="#fff" />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 14, color: '#f8fafc' }}>AI House Architect Studio</div>
            <div style={{ fontSize: 11, color: 'var(--color-primary)', fontFamily: 'JetBrains Mono, monospace' }}>
              {requirements.plot.width}ft × {requirements.plot.length}ft · {requirements.floors} Floor{requirements.floors > 1 ? 's' : ''} · {requirements.rooms.bedrooms}BR / {requirements.rooms.bathrooms}BA
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)', borderRadius: 8, padding: '5px 12px', fontSize: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
            <CheckCircle2 size={13} color="#34d399" />
            <span style={{ color: '#34d399', fontWeight: 600 }}>Concept #{selectedDesign.candidate_index + 1}</span>
            <span style={{ color: '#94a3b8' }}>· {(selectedDesign.quality_scores.overall_score * 100).toFixed(0)}% Score</span>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={onResetRequirements} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <RefreshCcw size={13} /> New Project
          </button>
        </div>
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

        {/* Sidebar */}
        <aside style={{ width: 220, background: 'rgba(11,16,29,0.8)', borderRight: '1px solid var(--color-border)', padding: 16, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', flexShrink: 0 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', padding: '0 8px', marginBottom: 8, fontFamily: 'monospace' }}>Navigation</div>
            {navItems.map(({ id, label, Icon }) => {
              const active = activeTab === id;
              return (
                <button
                  key={id}
                  onClick={() => setActiveTab(id)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '9px 12px', borderRadius: 10, border: 'none', cursor: 'pointer',
                    fontSize: 13, fontWeight: 600, transition: 'all 0.2s',
                    background: active ? 'rgba(99,102,241,0.2)' : 'transparent',
                    color: active ? '#a5b4fc' : 'var(--color-text-secondary)',
                    boxShadow: active ? 'var(--shadow-glow-sm)' : 'none',
                  }}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </button>
              );
            })}
          </div>
          <SafetyDisclaimer />
        </aside>

        {/* Main content */}
        <main style={{ flex: 1, overflowY: 'auto', padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
          {activeTab === '3d' && (
            <HouseViewer3D design={selectedDesign} onSelectRoom={setFocusedRoom} />
          )}
          {activeTab === 'comparison' && (
            <DesignComparison
              designs={designs}
              onSelectDesign={(d) => { setSelectedDesign(d); setActiveTab('3d'); }}
              onOpen3D={(d) => { setSelectedDesign(d); setActiveTab('3d'); }}
            />
          )}
          {activeTab === 'whatif' && (
            <WhatIfStudio
              currentRequirements={requirements}
              currentDesign={selectedDesign}
              onApplyRedesign={handleApplyRedesign}
            />
          )}
          {activeTab === 'analytics' && <AnalyticsDashboard />}
          {activeTab === 'evaluation' && <EvaluationPanel />}
        </main>

        {/* Right Inspector */}
        <aside style={{ width: 300, background: 'rgba(11,16,29,0.8)', borderLeft: '1px solid var(--color-border)', padding: 20, display: 'flex', flexDirection: 'column', gap: 20, flexShrink: 0, overflowY: 'auto' }}>

          {/* Design header */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <Building2 size={14} color="var(--color-primary)" />
              <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em', fontFamily: 'monospace' }}>Concept Inspector</span>
            </div>
            <div className="glass-card" style={{ padding: 14, borderRadius: 12 }}>
              <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 4 }}>Pareto Rank</div>
              <div style={{ fontSize: 20, fontWeight: 800, color: '#f8fafc', fontFamily: 'monospace' }}>#{selectedDesign.pareto_rank}</div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 8 }}>Total Area</div>
              <div style={{ fontSize: 16, fontWeight: 700, color: '#a5b4fc' }}>{selectedDesign.total_built_up_area.toFixed(0)} sq ft</div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 8 }}>Style</div>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#f8fafc', textTransform: 'capitalize' }}>{selectedDesign.architectural_style}</div>
            </div>
          </div>

          {/* Quality Scores */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
              <Layers size={14} color="var(--color-primary)" />
              <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em', fontFamily: 'monospace' }}>Quality Metrics</span>
            </div>
            <div className="glass-card" style={{ padding: 14, borderRadius: 12, display: 'flex', flexDirection: 'column', gap: 10 }}>
              <ScoreRow label="Space Efficiency"  value={qs.space_efficiency}  color="#6366f1" />
              <ScoreRow label="Natural Light"     value={qs.natural_light}     color="#f59e0b" />
              <ScoreRow label="Privacy Score"     value={qs.privacy_score}     color="#10b981" />
              <ScoreRow label="Circulation Flow"  value={qs.circulation_flow}  color="#06b6d4" />
              <ScoreRow label="Cultural Score"    value={qs.vastu_score}       color="#8b5cf6" />
              <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: 10 }}>
                <ScoreRow label="Overall Score"  value={qs.overall_score}     color="#ec4899" />
              </div>
            </div>
          </div>

          {/* Cost */}
          {selectedDesign.cost_estimate && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                <DollarSign size={14} color="#10b981" />
                <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em', fontFamily: 'monospace' }}>Cost Estimate</span>
              </div>
              <CostDisplay cost={selectedDesign.cost_estimate} />
            </div>
          )}

          {/* Cultural */}
          {selectedDesign.cultural_evaluation && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                <Compass size={14} color="#8b5cf6" />
                <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em', fontFamily: 'monospace' }}>Cultural Alignment</span>
              </div>
              <div className="glass-card" style={{ padding: 14, borderRadius: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                  <span style={{ fontSize: 12, fontWeight: 600, color: '#f8fafc', textTransform: 'capitalize' }}>{selectedDesign.cultural_evaluation.preference}</span>
                  <span style={{ fontFamily: 'monospace', fontWeight: 700, color: '#a78bfa', fontSize: 16 }}>
                    {(selectedDesign.cultural_evaluation.overall_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {selectedDesign.cultural_evaluation.recommendations.slice(0, 3).map((rec, i) => (
                    <div key={i} style={{ fontSize: 11, color: '#94a3b8', display: 'flex', gap: 6 }}>
                      <span style={{ color: '#8b5cf6', flexShrink: 0 }}>→</span>
                      <span>{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
};
