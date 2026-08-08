import React, { useState } from 'react';
import { DesignRequirement, CandidateDesign } from '../types';
import { Sliders, Sparkles, Loader2, ChevronRight } from 'lucide-react';

interface WhatIfStudioProps {
  currentRequirements: DesignRequirement;
  currentDesign:       CandidateDesign;
  onApplyRedesign:     (newDesigns: CandidateDesign[]) => void;
}

const QUICK_COMMANDS = [
  'Make the master bedroom 20% larger',
  'Add an extra bathroom on floor 2',
  'Increase kitchen area by 30 sq ft',
  'Expand the living room and open it to the dining',
  'Add a second balcony facing south',
  'Convert the home office into a 5th bedroom',
  'Increase parking to 3 cars',
  'Add a basement level for storage',
];

export const WhatIfStudio: React.FC<WhatIfStudioProps> = ({
  currentRequirements,
  currentDesign,
  onApplyRedesign,
}) => {
  const [command, setCommand]     = useState('');
  const [loading, setLoading]     = useState(false);
  const [result, setResult]       = useState<string | null>(null);
  const [error, setError]         = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!command.trim()) return;
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const res = await fetch('/api/v2/whatif-redesign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_requirements: currentRequirements,
          current_rooms:        currentDesign.rooms,
          action_command:       command,
        }),
      });
      const data = await res.json();
      if (data.status === 'success' && data.result) {
        const r = data.result;
        // Build updated designs list from returned modified rooms
        if (r.modified_rooms) {
          const updated: CandidateDesign = {
            ...currentDesign,
            rooms: r.modified_rooms,
            quality_scores: r.new_quality_scores ?? currentDesign.quality_scores,
            cost_estimate:  r.new_cost_estimate  ?? currentDesign.cost_estimate,
          };
          onApplyRedesign([updated]);
        }
        const changes = r.changes_applied ?? [];
        setResult(changes.length > 0 ? changes.join('\n') : 'Redesign applied successfully.');
      } else {
        setError(data.detail ?? 'Redesign returned no valid result.');
      }
    } catch (e) {
      setError('Network error — could not reach backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 700, display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h2 style={{ fontSize: 22, fontWeight: 800, color: '#f8fafc', marginBottom: 4 }}>What-If Redesign Studio</h2>
        <p style={{ fontSize: 13, color: '#94a3b8' }}>
          Describe a change in plain language — the AI will re-optimize the layout accordingly.
        </p>
      </div>

      {/* Command Input */}
      <div className="glass-card" style={{ padding: 20, borderRadius: 16 }}>
        <label className="input-label">Design Command</label>
        <textarea
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="e.g. Make the master bedroom larger and add an ensuite bathroom..."
          rows={3}
          style={{
            width: '100%', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--color-border)',
            borderRadius: 10, padding: '12px 14px', color: '#f8fafc', fontSize: 14,
            fontFamily: 'Inter, sans-serif', outline: 'none', resize: 'vertical',
            transition: 'border-color 0.15s',
          }}
          onFocus={(e) => e.target.style.borderColor = 'var(--color-primary)'}
          onBlur={(e) => e.target.style.borderColor = 'var(--color-border)'}
        />
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 12 }}>
          <button
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={loading || !command.trim()}
          >
            {loading
              ? <><Loader2 size={15} className="spin" /> Processing...</>
              : <><Sparkles size={15} /> Apply Redesign</>
            }
          </button>
        </div>
      </div>

      {/* Quick Commands */}
      <div>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 10, fontFamily: 'monospace' }}>
          Quick Suggestions
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {QUICK_COMMANDS.map((cmd) => (
            <button
              key={cmd}
              onClick={() => setCommand(cmd)}
              style={{
                background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.2)',
                borderRadius: 99, padding: '6px 14px', fontSize: 12, color: '#a5b4fc',
                cursor: 'pointer', transition: 'all 0.15s', display: 'flex', alignItems: 'center', gap: 5,
              }}
              onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(99,102,241,0.18)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(99,102,241,0.08)'; }}
            >
              <ChevronRight size={11} /> {cmd}
            </button>
          ))}
        </div>
      </div>

      {/* Result */}
      {result && (
        <div style={{
          background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.25)',
          borderRadius: 14, padding: 16, fontSize: 13, color: '#6ee7b7',
        }}>
          <div style={{ fontWeight: 700, marginBottom: 6, display: 'flex', gap: 6 }}>
            <Sparkles size={15} /> Changes Applied
          </div>
          <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: 12 }}>{result}</pre>
        </div>
      )}

      {error && (
        <div style={{
          background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)',
          borderRadius: 14, padding: 16, fontSize: 13, color: '#fca5a5',
        }}>
          {error}
        </div>
      )}
    </div>
  );
};
