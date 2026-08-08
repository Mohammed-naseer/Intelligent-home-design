import React, { useState } from 'react';
import { DesignRequirement } from '../types';
import {
  Compass,
  DollarSign,
  Maximize2,
  Layers,
  Sparkles,
  Bed,
  Bath,
  Utensils,
  Car,
  CheckCircle2,
  Building2,
  TreePine,
  Briefcase,
  Accessibility,
  TrendingUp,
} from 'lucide-react';

interface RequirementFormProps {
  onGenerate: (requirements: DesignRequirement) => void;
}

export const RequirementForm: React.FC<RequirementFormProps> = ({ onGenerate }) => {
  const [plotLength, setPlotLength] = useState<number>(60);
  const [plotWidth, setPlotWidth] = useState<number>(50);
  const [floors, setFloors] = useState<number>(2);

  const [bedrooms, setBedrooms] = useState<number>(4);
  const [bathrooms, setBathrooms] = useState<number>(3);
  const [kitchen, setKitchen] = useState<number>(1);
  const [parking, setParking] = useState<number>(2);
  const [balcony, setBalcony] = useState<number>(1);

  const [garden, setGarden] = useState<boolean>(true);
  const [homeOffice, setHomeOffice] = useState<boolean>(true);
  const [poojaRoom, setPoojaRoom] = useState<boolean>(false);

  const [budget, setBudget] = useState<'economy' | 'standard' | 'premium' | 'luxury'>('premium');
  const [style, setStyle] = useState<'modern' | 'traditional' | 'contemporary' | 'minimalist' | 'colonial'>('modern');
  const [climate, setClimate] = useState<'tropical' | 'temperate' | 'arid' | 'cold' | 'coastal'>('tropical');
  const [cultural, setCultural] = useState<'none' | 'vastu' | 'feng_shui' | 'qibla' | 'contemporary'>('vastu');

  const [accessibility, setAccessibility] = useState<boolean>(false);
  const [futureExpansion, setFutureExpansion] = useState<boolean>(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const reqs: DesignRequirement = {
      plot: { length: plotLength, width: plotWidth },
      floors,
      rooms: {
        bedrooms,
        bathrooms,
        kitchen,
        living_dining: 1,
        parking,
        balcony,
        garden,
        home_office: homeOffice,
        pooja_prayer_room: poojaRoom,
      },
      budget,
      architectural_style: style,
      climate_location: climate,
      cultural_preference: cultural,
      accessibility,
      future_expansion: futureExpansion,
    };
    onGenerate(reqs);
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-8 p-6 glass-card rounded-3xl border border-slate-800 shadow-2xl">
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Building2 className="w-5 h-5 text-indigo-400" /> Architectural Design Specification
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Configure plot geometry, floor counts, room requirements, and cultural orientation preferences.
        </p>
      </div>

      {/* Plot Geometry & Floor Count */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
          <Maximize2 className="w-4 h-4" /> 1. Plot Geometry & Floor Structure
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-2">
            <label className="text-xs text-slate-300 font-medium flex justify-between">
              <span>Plot Length (ft):</span>
              <span className="font-mono text-indigo-400 font-bold">{plotLength} ft</span>
            </label>
            <input
              type="range"
              min={25}
              max={150}
              value={plotLength}
              onChange={(e) => setPlotLength(Number(e.target.value))}
              className="w-full accent-indigo-500 bg-slate-800 rounded-lg cursor-pointer h-2"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs text-slate-300 font-medium flex justify-between">
              <span>Plot Width (ft):</span>
              <span className="font-mono text-indigo-400 font-bold">{plotWidth} ft</span>
            </label>
            <input
              type="range"
              min={20}
              max={150}
              value={plotWidth}
              onChange={(e) => setPlotWidth(Number(e.target.value))}
              className="w-full accent-indigo-500 bg-slate-800 rounded-lg cursor-pointer h-2"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs text-slate-300 font-medium flex justify-between">
              <span>Total Floors:</span>
              <span className="font-mono text-indigo-400 font-bold">{floors} Floor{floors > 1 ? 's' : ''}</span>
            </label>
            <div className="flex gap-2">
              {[1, 2, 3, 4].map((f) => (
                <button
                  type="button"
                  key={f}
                  onClick={() => setFloors(f)}
                  className={`flex-1 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                    floors === f
                      ? 'bg-indigo-600 text-white border-indigo-400'
                      : 'bg-dark-800 text-slate-400 border-slate-700 hover:text-white'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-dark-800/80 p-3 rounded-xl border border-slate-800 flex justify-between items-center text-xs">
          <span className="text-slate-400">Total Plot Footprint:</span>
          <span className="font-mono font-bold text-emerald-400">{plotLength * plotWidth} sq ft</span>
          <span className="text-slate-400">Max Build-up Potential:</span>
          <span className="font-mono font-bold text-indigo-400">{plotLength * plotWidth * floors} sq ft</span>
        </div>
      </div>

      {/* Room Program */}
      <div className="space-y-4 pt-4 border-t border-slate-800/80">
        <h3 className="text-sm font-semibold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
          <Bed className="w-4 h-4" /> 2. Room Schedule & Features
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-dark-800/60 p-3 rounded-xl border border-slate-800 space-y-1.5">
            <label className="text-xs text-slate-400 flex items-center gap-1">
              <Bed className="w-3.5 h-3.5 text-indigo-400" /> Bedrooms:
            </label>
            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={() => setBedrooms(Math.max(1, bedrooms - 1))}
                className="w-7 h-7 rounded-md bg-slate-800 hover:bg-slate-700 text-white font-bold"
              >
                -
              </button>
              <span className="font-mono text-sm font-bold text-white">{bedrooms}</span>
              <button
                type="button"
                onClick={() => setBedrooms(Math.min(10, bedrooms + 1))}
                className="w-7 h-7 rounded-md bg-slate-800 hover:bg-slate-700 text-white font-bold"
              >
                +
              </button>
            </div>
          </div>

          <div className="bg-dark-800/60 p-3 rounded-xl border border-slate-800 space-y-1.5">
            <label className="text-xs text-slate-400 flex items-center gap-1">
              <Bath className="w-3.5 h-3.5 text-cyan-400" /> Bathrooms:
            </label>
            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={() => setBathrooms(Math.max(1, bathrooms - 1))}
                className="w-7 h-7 rounded-md bg-slate-800 hover:bg-slate-700 text-white font-bold"
              >
                -
              </button>
              <span className="font-mono text-sm font-bold text-white">{bathrooms}</span>
              <button
                type="button"
                onClick={() => setBathrooms(Math.min(10, bathrooms + 1))}
                className="w-7 h-7 rounded-md bg-slate-800 hover:bg-slate-700 text-white font-bold"
              >
                +
              </button>
            </div>
          </div>

          <div className="bg-dark-800/60 p-3 rounded-xl border border-slate-800 space-y-1.5">
            <label className="text-xs text-slate-400 flex items-center gap-1">
              <Car className="w-3.5 h-3.5 text-amber-400" /> Parking:
            </label>
            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={() => setParking(Math.max(0, parking - 1))}
                className="w-7 h-7 rounded-md bg-slate-800 hover:bg-slate-700 text-white font-bold"
              >
                -
              </button>
              <span className="font-mono text-sm font-bold text-white">{parking}</span>
              <button
                type="button"
                onClick={() => setParking(Math.min(5, parking + 1))}
                className="w-7 h-7 rounded-md bg-slate-800 hover:bg-slate-700 text-white font-bold"
              >
                +
              </button>
            </div>
          </div>

          <div className="bg-dark-800/60 p-3 rounded-xl border border-slate-800 space-y-1.5">
            <label className="text-xs text-slate-400 flex items-center gap-1">
              <Utensils className="w-3.5 h-3.5 text-emerald-400" /> Kitchens:
            </label>
            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={() => setKitchen(Math.max(1, kitchen - 1))}
                className="w-7 h-7 rounded-md bg-slate-800 hover:bg-slate-700 text-white font-bold"
              >
                -
              </button>
              <span className="font-mono text-sm font-bold text-white">{kitchen}</span>
              <button
                type="button"
                onClick={() => setKitchen(Math.min(3, kitchen + 1))}
                className="w-7 h-7 rounded-md bg-slate-800 hover:bg-slate-700 text-white font-bold"
              >
                +
              </button>
            </div>
          </div>
        </div>

        {/* Feature Checkboxes */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2">
          <label className={`p-3 rounded-xl border flex items-center gap-2 cursor-pointer transition-all ${garden ? 'bg-indigo-950/60 border-indigo-500/50 text-white' : 'bg-dark-800/40 border-slate-800 text-slate-400'}`}>
            <input type="checkbox" checked={garden} onChange={(e) => setGarden(e.target.checked)} className="hidden" />
            <TreePine className="w-4 h-4 text-emerald-400" /> <span className="text-xs">Garden / Yard</span>
          </label>

          <label className={`p-3 rounded-xl border flex items-center gap-2 cursor-pointer transition-all ${homeOffice ? 'bg-indigo-950/60 border-indigo-500/50 text-white' : 'bg-dark-800/40 border-slate-800 text-slate-400'}`}>
            <input type="checkbox" checked={homeOffice} onChange={(e) => setHomeOffice(e.target.checked)} className="hidden" />
            <Briefcase className="w-4 h-4 text-indigo-400" /> <span className="text-xs">Home Office</span>
          </label>

          <label className={`p-3 rounded-xl border flex items-center gap-2 cursor-pointer transition-all ${poojaRoom ? 'bg-indigo-950/60 border-indigo-500/50 text-white' : 'bg-dark-800/40 border-slate-800 text-slate-400'}`}>
            <input type="checkbox" checked={poojaRoom} onChange={(e) => setPoojaRoom(e.target.checked)} className="hidden" />
            <Compass className="w-4 h-4 text-amber-400" /> <span className="text-xs">Prayer / Pooja Room</span>
          </label>
        </div>
      </div>

      {/* Style, Budget, Cultural & Special Options */}
      <div className="space-y-4 pt-4 border-t border-slate-800/80">
        <h3 className="text-sm font-semibold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
          <Compass className="w-4 h-4" /> 3. Style, Budget & Cultural Preferences
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Architectural Style */}
          <div className="space-y-2">
            <label className="text-xs text-slate-300 font-medium">Architectural Style:</label>
            <select
              value={style}
              onChange={(e) => setStyle(e.target.value as any)}
              className="w-full bg-dark-800 border border-slate-700 rounded-xl p-2.5 text-xs text-white focus:ring-2 focus:ring-indigo-500 outline-none"
            >
              <option value="modern">Modern Minimalist</option>
              <option value="contemporary">Contemporary Luxury</option>
              <option value="traditional">Traditional Villa</option>
              <option value="minimalist">Minimalist Japanese</option>
              <option value="colonial">Colonial Estate</option>
            </select>
          </div>

          {/* Budget Tier */}
          <div className="space-y-2">
            <label className="text-xs text-slate-300 font-medium">Budget Tier:</label>
            <select
              value={budget}
              onChange={(e) => setBudget(e.target.value as any)}
              className="w-full bg-dark-800 border border-slate-700 rounded-xl p-2.5 text-xs text-white focus:ring-2 focus:ring-indigo-500 outline-none"
            >
              <option value="economy">Economy Standard</option>
              <option value="standard">Standard Quality</option>
              <option value="premium">Premium Architectural</option>
              <option value="luxury">High-End Luxury</option>
            </select>
          </div>

          {/* Cultural Preferences */}
          <div className="space-y-2">
            <label className="text-xs text-slate-300 font-medium">Cultural Alignment:</label>
            <select
              value={cultural}
              onChange={(e) => setCultural(e.target.value as any)}
              className="w-full bg-dark-800 border border-slate-700 rounded-xl p-2.5 text-xs text-white focus:ring-2 focus:ring-indigo-500 outline-none"
            >
              <option value="none">None (Standard Ergonomics)</option>
              <option value="vastu">Vastu Shastra Principles</option>
              <option value="feng_shui">Feng Shui Bagua Flow</option>
              <option value="qibla">Qibla & Privacy Zoning</option>
              <option value="contemporary">Contemporary Open-Concept</option>
            </select>
          </div>
        </div>

        {/* Accessibility & Future Expansion */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          <label className={`p-3 rounded-xl border flex items-center gap-3 cursor-pointer transition-all ${accessibility ? 'bg-indigo-950/60 border-indigo-500/50 text-white' : 'bg-dark-800/40 border-slate-800 text-slate-400'}`}>
            <input type="checkbox" checked={accessibility} onChange={(e) => setAccessibility(e.target.checked)} className="hidden" />
            <Accessibility className="w-5 h-5 text-indigo-400 shrink-0" />
            <div className="text-xs">
              <div className="font-semibold text-white">Wheelchair Accessibility</div>
              <div className="text-[11px] text-slate-400">Step-free ground floor & 4ft wider corridors</div>
            </div>
          </label>

          <label className={`p-3 rounded-xl border flex items-center gap-3 cursor-pointer transition-all ${futureExpansion ? 'bg-indigo-950/60 border-indigo-500/50 text-white' : 'bg-dark-800/40 border-slate-800 text-slate-400'}`}>
            <input type="checkbox" checked={futureExpansion} onChange={(e) => setFutureExpansion(e.target.checked)} className="hidden" />
            <TrendingUp className="w-5 h-5 text-emerald-400 shrink-0" />
            <div className="text-xs">
              <div className="font-semibold text-white">Future Vertical Expansion</div>
              <div className="text-[11px] text-slate-400">Design structural provision for additional floor</div>
            </div>
          </label>
        </div>
      </div>

      {/* Submit Button */}
      <div className="pt-4 border-t border-slate-800/80 flex justify-end">
        <button
          type="submit"
          className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-sm shadow-xl glow-indigo transition-all flex items-center justify-center gap-2"
        >
          <Sparkles className="w-4 h-4 text-white" /> Generate Candidate Designs
        </button>
      </div>
    </form>
  );
};
