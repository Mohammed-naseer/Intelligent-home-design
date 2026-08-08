import React from 'react';
import { Hero3DCanvas } from './Hero3DCanvas';
import { Showcase3DStudio } from './Showcase3DStudio';
import { UserSession } from './AuthModal';
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Layers,
  Compass,
  Sliders,
  DollarSign,
  BarChart3,
  Box,
  CheckCircle2,
  User as UserIcon,
  LogOut,
  Star,
  Zap,
  Globe,
  FileText,
} from 'lucide-react';

interface LandingPageProps {
  onStartDesigning: () => void;
  onExploreDemo: () => void;
  onOpenAuth: (mode: 'login' | 'register') => void;
  user: UserSession | null;
  onLogout: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onStartDesigning,
  onExploreDemo,
  onOpenAuth,
  user,
  onLogout,
}) => {
  return (
    <div className="relative min-h-screen bg-dark-950 text-slate-100 overflow-x-hidden flex flex-col justify-between">
      {/* Background Decorative Grids & Glass Orbs */}
      <div className="absolute top-0 left-1/4 w-[700px] h-[700px] bg-indigo-600/10 rounded-full blur-[160px] pointer-events-none" />
      <div className="absolute top-1/2 right-1/4 w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[160px] pointer-events-none" />
      <div className="absolute bottom-0 left-1/3 w-[500px] h-[500px] bg-emerald-600/10 rounded-full blur-[160px] pointer-events-none" />

      {/* ── Top Header Navigation Bar ────────────────────────────────────────────── */}
      <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-dark-950/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          {/* Logo & Platform Name */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg glow-indigo">
              <Box className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-tight text-white font-sans flex items-center gap-2">
                NeuroArch<span className="text-indigo-400 font-mono text-xs px-1.5 py-0.5 rounded bg-indigo-950 border border-indigo-500/30">3D AI</span>
              </h1>
              <p className="text-[11px] text-slate-400 font-mono tracking-wide">
                ADAPTIVE ARCHITECTURAL PLATFORM
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-8 text-xs font-medium text-slate-300">
            <a href="#hero" className="hover:text-white transition-colors">3D Engine</a>
            <a href="#showcase" className="hover:text-white transition-colors">Architectures</a>
            <a href="#features" className="hover:text-white transition-colors">AI Pipeline</a>
            <a href="#pricing" className="hover:text-white transition-colors">Plans</a>
            <a href="/docs" target="_blank" rel="noreferrer" className="hover:text-white transition-colors flex items-center gap-1">
              <FileText className="w-3.5 h-3.5 text-indigo-400" /> API Docs
            </a>
          </nav>

          {/* User Auth Buttons / Profile */}
          <div className="flex items-center gap-3">
            {user && user.isAuth ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-dark-900 border border-slate-800">
                  <img src={user.avatar} alt={user.name} className="w-7 h-7 rounded-full object-cover border border-indigo-500" />
                  <div className="text-left">
                    <div className="text-xs font-bold text-white leading-none">{user.name}</div>
                    <div className="text-[10px] text-indigo-400 leading-none mt-1">{user.role}</div>
                  </div>
                </div>
                <button
                  onClick={onLogout}
                  className="p-2 rounded-xl bg-dark-900 border border-slate-800 text-slate-400 hover:text-red-400 transition-colors"
                  title="Sign Out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <>
                <button
                  onClick={() => onOpenAuth('login')}
                  className="text-xs font-semibold px-4 py-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800/80 transition-all border border-slate-800"
                >
                  Sign In
                </button>
                <button
                  onClick={onStartDesigning}
                  className="text-xs font-semibold px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-lg glow-indigo flex items-center gap-2"
                >
                  Start 3D Design <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* ── Main Hero Section ────────────────────────────────────────────────── */}
      <main id="hero" className="relative z-10 max-w-7xl w-full mx-auto px-6 py-12 my-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Hero Text Column */}
          <div className="lg:col-span-6 space-y-8">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-950/80 border border-indigo-500/30 text-indigo-300 text-xs font-medium">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              <span>PyTorch Neural Network + Shapely Geometry Engine</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.1] font-sans">
              Autonomous Residential Architecture in <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-300 to-pink-400">Interactive 3D</span>
            </h1>

            <p className="text-base sm:text-lg text-slate-300 font-light leading-relaxed">
              Transform your plot constraints, budget, and cultural preferences into an intelligent 3D house model. Evaluated with local deep learning models, zero external API keys, and Pareto multi-objective optimization.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button
                onClick={onStartDesigning}
                className="px-7 py-3.5 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-sm shadow-xl glow-indigo transition-all flex items-center gap-2.5"
              >
                Start Designing <ArrowRight className="w-4 h-4" />
              </button>
              <button
                onClick={onExploreDemo}
                className="px-7 py-3.5 rounded-2xl glass-card text-slate-200 hover:text-white font-semibold text-sm transition-all border border-slate-700/80 hover:bg-slate-800 flex items-center gap-2"
              >
                <Zap className="w-4 h-4 text-emerald-400" /> Instant 3D Demo
              </button>
            </div>

            {/* Platform Telemetry Badges */}
            <div className="pt-6 border-t border-slate-800/80 grid grid-cols-3 gap-6">
              <div>
                <div className="text-2xl font-bold text-white font-mono">100% Local</div>
                <div className="text-xs text-slate-400">Zero Cloud API Costs</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-emerald-400 font-mono">94.2%</div>
                <div className="text-xs text-slate-400">Valid Layout Rate</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-indigo-400 font-mono">&lt;250 ms</div>
                <div className="text-xs text-slate-400">Generation Latency</div>
              </div>
            </div>
          </div>

          {/* Right Hero Column: Interactive 3D Three.js Canvas */}
          <div className="lg:col-span-6">
            <Hero3DCanvas />
          </div>
        </div>
      </main>

      {/* ── 3D Archetype Showcase Section ────────────────────────────────────── */}
      <div id="showcase">
        <Showcase3DStudio onSelectPreset={() => onStartDesigning()} />
      </div>

      {/* ── AI Engine Features Section ────────────────────────────────────────── */}
      <section id="features" className="py-20 relative z-10 border-t border-slate-800/80">
        <div className="max-w-7xl mx-auto px-6 space-y-12">
          <div className="text-center space-y-4 max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-purple-950/80 border border-purple-500/30 text-purple-300 text-xs font-medium">
              <Cpu className="w-3.5 h-3.5 text-purple-400" />
              <span>Full Stack Local Machine Learning</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Architectural Precision Powered By <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-300 to-pink-400">4 Core Engines</span>
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="glass-card p-6 rounded-3xl border border-slate-800 hover:border-indigo-500/50 transition-all space-y-4 group">
              <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
                <Cpu className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-white">PyTorch Layout NN</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Deep neural network trained on architectural floor plans predicting room positions, dimensions, and spatial adjacency.
              </p>
            </div>

            <div className="glass-card p-6 rounded-3xl border border-slate-800 hover:border-emerald-500/50 transition-all space-y-4 group">
              <div className="w-12 h-12 rounded-2xl bg-emerald-600/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
                <Layers className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-white">Shapely Geometry</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Polygon constraint engine guaranteeing zero room overlap, setback validation, and plot boundary enforcement.
              </p>
            </div>

            <div className="glass-card p-6 rounded-3xl border border-slate-800 hover:border-purple-500/50 transition-all space-y-4 group">
              <div className="w-12 h-12 rounded-2xl bg-purple-600/20 border border-purple-500/40 flex items-center justify-center text-purple-400 group-hover:scale-110 transition-transform">
                <Sliders className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-white">Pareto Optimizer</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Multi-objective optimization scoring space utilization, circulation flow, natural lighting, and privacy levels.
              </p>
            </div>

            <div className="glass-card p-6 rounded-3xl border border-slate-800 hover:border-pink-500/50 transition-all space-y-4 group">
              <div className="w-12 h-12 rounded-2xl bg-pink-600/20 border border-pink-500/40 flex items-center justify-center text-pink-400 group-hover:scale-110 transition-transform">
                <Compass className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-white">Cultural Evaluator</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Rules-based evaluation for Vastu Shastra, Feng Shui, Qibla orientation, and modern architectural guidelines.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Pricing Tiers Section ────────────────────────────────────────────── */}
      <section id="pricing" className="py-20 relative z-10 border-t border-slate-800/80">
        <div className="max-w-7xl mx-auto px-6 space-y-12">
          <div className="text-center space-y-4 max-w-3xl mx-auto">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Flexible Architectural Plans
            </h2>
            <p className="text-sm text-slate-400">
              Select the plan tailored to your residential projects or enterprise studio workflow.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Starter Plan */}
            <div className="glass-card p-8 rounded-3xl border border-slate-800 space-y-6 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Community Starter</div>
                <div className="text-4xl font-extrabold text-white font-mono">$0 <span className="text-xs text-slate-400 font-sans">/ forever free</span></div>
                <p className="text-xs text-slate-400">Ideal for homeowners exploring initial plot layouts and 3D previews.</p>
                <ul className="space-y-2.5 text-xs text-slate-300 pt-4 border-t border-slate-800">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> 15 AI Layout Candidates / Request</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Interactive 3D Model Viewer</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Vastu Alignment Scoring</li>
                </ul>
              </div>
              <button
                onClick={onStartDesigning}
                className="w-full py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-all"
              >
                Get Started Free
              </button>
            </div>

            {/* Pro Architect Plan */}
            <div className="glass-card p-8 rounded-3xl border border-indigo-500/60 shadow-2xl glow-indigo space-y-6 flex flex-col justify-between relative">
              <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-indigo-600 text-white text-[10px] font-bold uppercase tracking-wider">
                Most Popular
              </div>
              <div className="space-y-4">
                <div className="text-sm font-semibold text-indigo-400 uppercase tracking-wider">Pro Architect</div>
                <div className="text-4xl font-extrabold text-white font-mono">$49 <span className="text-xs text-slate-400 font-sans">/ month</span></div>
                <p className="text-xs text-slate-400">For practicing architects needing high-DPI exports & What-If studio.</p>
                <ul className="space-y-2.5 text-xs text-slate-300 pt-4 border-t border-slate-800">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Unlimited What-If Redesigns</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> High-DPI PNG & SVG Exports</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Full Cost Estimator Engine</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Model Retraining Integration</li>
                </ul>
              </div>
              <button
                onClick={() => onOpenAuth('register')}
                className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg transition-all"
              >
                Upgrade to Pro
              </button>
            </div>

            {/* Enterprise Studio Plan */}
            <div className="glass-card p-8 rounded-3xl border border-slate-800 space-y-6 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="text-sm font-semibold text-purple-400 uppercase tracking-wider">Enterprise Studio</div>
                <div className="text-4xl font-extrabold text-white font-mono">$199 <span className="text-xs text-slate-400 font-sans">/ month</span></div>
                <p className="text-xs text-slate-400">Custom ML training on studio proprietary architectural dataset.</p>
                <ul className="space-y-2.5 text-xs text-slate-300 pt-4 border-t border-slate-800">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Dedicated FastMCP Server</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Custom Neural Layout Weights</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Multi-user License & Telemetry</li>
                </ul>
              </div>
              <button
                onClick={() => onOpenAuth('register')}
                className="w-full py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-all"
              >
                Contact Enterprise
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ──────────────────────────────────────────────────────────── */}
      <footer className="relative z-10 border-t border-slate-800/80 bg-dark-950 py-12">
        <div className="max-w-7xl mx-auto px-6 space-y-8">
          <div className="flex flex-wrap items-center justify-between gap-6 border-b border-slate-800 pb-8">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <Box className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="font-bold text-base text-white">NeuroArchAI Platform</span>
                <p className="text-xs text-slate-400">Autonomous 3D Architectural Design System</p>
              </div>
            </div>

            <div className="flex items-center gap-6 text-xs text-slate-400">
              <a href="/docs" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">Swagger API</a>
              <a href="/redoc" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">ReDoc</a>
              <a href="#hero" className="hover:text-white transition-colors">Back to Top</a>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
            <div>© 2026 NeuroArchAI Platform. MIT Licensed Open Source.</div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span>Local PyTorch & Scikit-Learn Engine Active</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};
