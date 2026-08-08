import React, { useState } from 'react';
import { Sparkles, Layers, Box, Check, Eye, Maximize2, Compass, ShieldCheck } from 'lucide-react';

interface Preset {
  id: string;
  name: string;
  tagline: string;
  floors: number;
  area: string;
  style: string;
  vastuScore: string;
  color: string;
  accentColor: string;
  rooms: string[];
}

const PRESETS: Preset[] = [
  {
    id: 'modern-villa',
    name: 'Neo-Modern Executive Villa',
    tagline: 'Dual-level open cantilever with solar roof & floor-to-ceiling glass',
    floors: 2,
    area: '3,400 sq.ft',
    style: 'Modern Minimalist',
    vastuScore: '94.5%',
    color: '#6366f1',
    accentColor: 'indigo',
    rooms: ['4 Master Bedrooms', '3 Bathrooms', 'Sky Terrace', 'Double Garage', 'Home Office'],
  },
  {
    id: 'eco-mansion',
    name: 'Biophilic Eco Sanctuary',
    tagline: 'Passive solar design with integrated interior courtyard & rainwater grid',
    floors: 3,
    area: '4,800 sq.ft',
    style: 'Contemporary Biophilic',
    vastuScore: '98.0%',
    color: '#10b981',
    accentColor: 'emerald',
    rooms: ['5 Bedrooms', '4.5 Baths', 'Atrium Garden', 'Solar Deck', 'Private Pool'],
  },
  {
    id: 'vastu-haven',
    name: 'Vastu Shastra Horizon',
    tagline: 'Oriented north-east entrance, auspicious kitchen & master placement',
    floors: 2,
    area: '2,900 sq.ft',
    style: 'Traditional Indo-Fusion',
    vastuScore: '100%',
    color: '#8b5cf6',
    accentColor: 'purple',
    rooms: ['3 Bedrooms', '3 Baths', 'Pooja Prayer Room', 'Verandah', 'Courtyard'],
  },
];

export const Showcase3DStudio: React.FC<{ onSelectPreset: (presetId: string) => void }> = ({ onSelectPreset }) => {
  const [selectedId, setSelectedId] = useState<string>('modern-villa');
  const activePreset = PRESETS.find((p) => p.id === selectedId) || PRESETS[0];

  return (
    <section className="py-20 relative z-10">
      <div className="max-w-7xl mx-auto px-6 space-y-12">
        {/* Section Heading */}
        <div className="text-center space-y-4 max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-950/80 border border-indigo-500/30 text-indigo-300 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Interactive 3D Architectural Catalog</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Explore Pre-Trained <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-300 to-pink-400">3D Design Archetypes</span>
          </h2>
          <p className="text-sm text-slate-400">
            Select a candidate architectural blueprint to preview spatial arrangement, material finishes, and cultural compliance scores in real-time.
          </p>
        </div>

        {/* Studio Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
          {/* Preset Selector List */}
          <div className="lg:col-span-5 space-y-4 flex flex-col justify-between">
            <div className="space-y-3">
              {PRESETS.map((preset) => {
                const isSelected = preset.id === selectedId;
                return (
                  <button
                    key={preset.id}
                    onClick={() => setSelectedId(preset.id)}
                    className={`w-full text-left p-5 rounded-2xl transition-all border ${
                      isSelected
                        ? 'glass-card border-indigo-500/60 shadow-xl glow-indigo bg-indigo-950/30'
                        : 'bg-dark-900/60 hover:bg-dark-800/80 border-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <h3 className={`font-bold text-base ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                        {preset.name}
                      </h3>
                      {isSelected && (
                        <div className="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs">
                          <Check className="w-3.5 h-3.5" />
                        </div>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-2">{preset.tagline}</p>
                    <div className="flex items-center gap-4 mt-3 text-[11px] font-mono">
                      <span className="text-indigo-400 font-semibold">{preset.area}</span>
                      <span className="text-slate-500">•</span>
                      <span className="text-emerald-400 font-semibold">{preset.vastuScore} Vastu</span>
                    </div>
                  </button>
                );
              })}
            </div>

            <button
              onClick={() => onSelectPreset(selectedId)}
              className="w-full py-4 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-sm shadow-xl glow-indigo transition-all flex items-center justify-center gap-2"
            >
              <Box className="w-4 h-4" /> Load Archetype into 3D Workspace
            </button>
          </div>

          {/* Interactive 3D Card Display */}
          <div className="lg:col-span-7">
            <div className="h-full glass-card p-7 rounded-3xl border border-slate-700/80 shadow-2xl flex flex-col justify-between relative overflow-hidden">
              <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-600/10 rounded-full blur-[100px] pointer-events-none" />

              {/* Archetype Header */}
              <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-5">
                <div>
                  <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <Box className="w-5 h-5 text-indigo-400" /> {activePreset.name}
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">{activePreset.style}</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="px-3 py-1 rounded-xl bg-dark-900 border border-slate-800 text-xs font-mono text-indigo-300">
                    {activePreset.floors} Floors
                  </div>
                  <div className="px-3 py-1 rounded-xl bg-emerald-950 border border-emerald-500/40 text-xs font-mono text-emerald-400">
                    {activePreset.vastuScore} Compliance
                  </div>
                </div>
              </div>

              {/* 3D Representation Box */}
              <div className="my-6 aspect-[16/9] rounded-2xl bg-dark-950 border border-slate-800 p-6 flex flex-col justify-center items-center relative overflow-hidden group">
                <div className="absolute inset-0 opacity-15 bg-[radial-gradient(#818cf8_1px,transparent_1px)] [background-size:20px_20px]" />

                {/* Isometric Box Animation */}
                <div className="relative z-10 text-center space-y-3 transition-transform duration-500 group-hover:scale-105">
                  <div className="w-24 h-24 mx-auto rounded-3xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center glow-indigo shadow-2xl">
                    <Box className="w-12 h-12 text-indigo-400 animate-bounce" />
                  </div>
                  <div className="text-xs font-mono text-slate-300">
                    Rendering 3D Mesh Geometry [{activePreset.id}]
                  </div>
                </div>

                <div className="absolute bottom-3 left-3 bg-dark-900/90 border border-slate-800 px-3 py-1 rounded-lg text-[11px] font-mono text-slate-400">
                  Built-up: {activePreset.area}
                </div>
              </div>

              {/* Room Components */}
              <div className="space-y-3">
                <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Included Spatial Program:
                </div>
                <div className="flex flex-wrap gap-2">
                  {activePreset.rooms.map((room, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1.5 rounded-xl bg-dark-800/80 border border-slate-800 text-xs text-slate-200 flex items-center gap-1.5"
                    >
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      {room}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
