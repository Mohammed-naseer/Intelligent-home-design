import React, { useState } from 'react';
import {
  X,
  Lock,
  Mail,
  User,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  Github,
  Globe,
  Building2,
  Compass,
  Briefcase,
  CheckCircle2,
  Key,
} from 'lucide-react';

export interface UserSession {
  name: string;
  email: string;
  role: string;
  avatar: string;
  isAuth: boolean;
}

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (user: UserSession) => void;
  initialMode?: 'login' | 'register';
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  onLoginSuccess,
  initialMode = 'login',
}) => {
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);
  const [email, setEmail] = useState<string>('architect@neuroarch.ai');
  const [password, setPassword] = useState<string>('••••••••••••');
  const [fullName, setFullName] = useState<string>('Alex Mercer');
  const [role, setRole] = useState<string>('Senior Architect');
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>('');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    if (!email || !password) {
      setErrorMsg('Please provide valid credentials.');
      return;
    }

    setLoading(true);

    // Simulate authenticating session
    setTimeout(() => {
      setLoading(false);
      const user: UserSession = {
        name: mode === 'register' ? fullName : email.split('@')[0].replace('.', ' '),
        email,
        role: mode === 'register' ? role : 'Lead Architect',
        avatar: `https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80`,
        isAuth: true,
      };
      onLoginSuccess(user);
      onClose();
    }, 800);
  };

  const handleQuickDemoAuth = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      const user: UserSession = {
        name: 'Demo Architect',
        email: 'demo@neuroarch.ai',
        role: 'Principal Architectural Designer',
        avatar: `https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80`,
        isAuth: true,
      };
      onLoginSuccess(user);
      onClose();
    }, 600);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-dark-950/80 backdrop-blur-xl animate-fade-in">
      {/* 3D Backdrop Glows */}
      <div className="absolute top-1/3 left-1/3 w-96 h-96 bg-indigo-600/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/3 right-1/3 w-80 h-80 bg-purple-600/20 rounded-full blur-[120px] pointer-events-none" />

      {/* Main Glassmorphic 3D Card */}
      <div className="relative w-full max-w-md glass-card rounded-3xl border border-indigo-500/30 p-8 shadow-2xl overflow-hidden space-y-6">
        {/* Decorative Top Accent Bar */}
        <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500" />

        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/60 transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/80 border border-indigo-500/30 text-indigo-300 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Secure 3D Workspace Auth</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">
            {mode === 'login' ? 'Welcome Back' : 'Create 3D Architect Account'}
          </h2>
          <p className="text-xs text-slate-400">
            {mode === 'login'
              ? 'Access saved 3D floor plans, custom materials & offline ML pipelines.'
              : 'Join the platform to orchestrate AI layout engines & 3D models.'}
          </p>
        </div>

        {/* Tabs Switcher */}
        <div className="flex bg-dark-900/90 border border-slate-800 p-1 rounded-2xl text-xs font-semibold">
          <button
            type="button"
            onClick={() => setMode('login')}
            className={`flex-1 py-2.5 rounded-xl transition-all ${
              mode === 'login'
                ? 'bg-indigo-600 text-white shadow-lg'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => setMode('register')}
            className={`flex-1 py-2.5 rounded-xl transition-all ${
              mode === 'register'
                ? 'bg-indigo-600 text-white shadow-lg'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Register
          </button>
        </div>

        {errorMsg && (
          <div className="p-3 rounded-xl bg-red-950/60 border border-red-500/40 text-red-300 text-xs flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 shrink-0 text-red-400" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Form Inputs */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-300">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Elena Rostova"
                    className="w-full bg-dark-900/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-300">Professional Role</label>
                <div className="relative">
                  <Briefcase className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full bg-dark-900/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition-all"
                  >
                    <option value="Residential Architect">Residential Architect</option>
                    <option value="Interior Designer">Interior Designer</option>
                    <option value="Structural Engineer">Structural Engineer</option>
                    <option value="Property Developer">Property Developer</option>
                    <option value="Homeowner">Homeowner / Enthusiast</option>
                  </select>
                </div>
              </div>
            </>
          )}

          <div className="space-y-1.5">
            <label className="text-xs font-medium text-slate-300">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="architect@domain.com"
                className="w-full bg-dark-900/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-slate-300">Password</label>
              {mode === 'login' && (
                <a href="#forgot" onClick={(e) => e.preventDefault()} className="text-[11px] text-indigo-400 hover:underline">
                  Forgot?
                </a>
              )}
            </div>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-dark-900/80 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all"
              />
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs shadow-lg glow-indigo transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <span>{mode === 'login' ? 'Sign In to 3D Workspace' : 'Create Architect Account'}</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Divider */}
        <div className="relative flex items-center justify-center">
          <div className="w-full border-t border-slate-800" />
          <span className="absolute bg-dark-950 px-3 text-[10px] uppercase tracking-wider text-slate-500 font-mono">
            Or quick demo access
          </span>
        </div>

        {/* Quick Demo & Social Login */}
        <div className="space-y-2.5">
          <button
            type="button"
            onClick={handleQuickDemoAuth}
            className="w-full py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 hover:text-white font-semibold text-xs transition-all flex items-center justify-center gap-2"
          >
            <Key className="w-4 h-4 text-emerald-400" />
            <span>Continue as Guest Architect (Instant)</span>
          </button>
        </div>

        {/* Bottom Trust Disclaimer */}
        <div className="text-center pt-2 text-[10px] text-slate-500 flex items-center justify-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Local execution — No credentials shared externally</span>
        </div>
      </div>
    </div>
  );
};
