import React, { useState, useEffect } from 'react';
import { LandingPage } from './components/LandingPage';
import { AuthModal, UserSession } from './components/AuthModal';
import { RequirementForm } from './components/RequirementForm';
import { GenerationProgress } from './components/GenerationProgress';
import { DesignWorkspace } from './components/DesignWorkspace';
import { DesignRequirement, CandidateDesign } from './types';
import { Box, LogOut, ArrowLeft, User as UserIcon, Sparkles } from 'lucide-react';

export const App: React.FC = () => {
  const [viewState, setViewState] = useState<'landing' | 'requirements' | 'progress' | 'workspace'>('landing');
  const [requirements, setRequirements] = useState<DesignRequirement | null>(null);
  const [candidateDesigns, setCandidateDesigns] = useState<CandidateDesign[]>([]);

  // Auth State
  const [isAuthOpen, setIsAuthOpen] = useState<boolean>(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [user, setUser] = useState<UserSession | null>(null);

  // Restore user session from localStorage if present
  useEffect(() => {
    const savedUser = localStorage.getItem('neuroarch_user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (e) {
        console.error('Failed to parse user session:', e);
      }
    }
  }, []);

  const handleOpenAuth = (mode: 'login' | 'register' = 'login') => {
    setAuthMode(mode);
    setIsAuthOpen(true);
  };

  const handleLoginSuccess = (userSession: UserSession) => {
    setUser(userSession);
    localStorage.setItem('neuroarch_user', JSON.stringify(userSession));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('neuroarch_user');
  };

  const handleStartDesigning = () => {
    setViewState('requirements');
  };

  const handleExploreDemo = async () => {
    const defaultReq: DesignRequirement = {
      plot: { length: 60, width: 50 },
      floors: 2,
      rooms: {
        bedrooms: 4,
        bathrooms: 3,
        kitchen: 1,
        living_dining: 1,
        parking: 2,
        balcony: 1,
        garden: true,
        home_office: true,
        pooja_prayer_room: false,
      },
      budget: 'premium',
      architectural_style: 'modern',
      climate_location: 'tropical',
      cultural_preference: 'vastu',
      accessibility: false,
      future_expansion: false,
    };
    setRequirements(defaultReq);
    setViewState('progress');
    await triggerGeneration(defaultReq);
  };

  const handleFormSubmit = async (reqs: DesignRequirement) => {
    setRequirements(reqs);
    setViewState('progress');
    await triggerGeneration(reqs);
  };

  const triggerGeneration = async (reqs: DesignRequirement) => {
    try {
      const res = await fetch('/api/v2/generate-designs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reqs),
      });
      const data = await res.json();
      if (data.status === 'success' && data.designs) {
        setCandidateDesigns(data.designs);
      }
    } catch (e) {
      console.error('Generation error:', e);
    }
  };

  const handleProgressComplete = () => {
    setViewState('workspace');
  };

  return (
    <div className="min-h-screen bg-dark-950 text-slate-100 font-sans selection:bg-indigo-500 selection:text-white flex flex-col justify-between">
      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onLoginSuccess={handleLoginSuccess}
        initialMode={authMode}
      />

      {/* Workspace Header for Non-Landing Views */}
      {viewState !== 'landing' && (
        <header className="z-30 w-full border-b border-slate-800 bg-dark-950/90 backdrop-blur-md px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setViewState('landing')}
              className="px-3 py-1.5 rounded-xl bg-dark-900 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-white flex items-center gap-1.5 transition-all"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Landing Page
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center">
                <Box className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-sm text-white">NeuroArch 3D Studio</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {user && user.isAuth ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 px-3 py-1 rounded-xl bg-dark-900 border border-slate-800">
                  <img src={user.avatar} alt={user.name} className="w-6 h-6 rounded-full object-cover border border-indigo-500" />
                  <span className="text-xs font-semibold text-white">{user.name}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-1.5 rounded-xl text-slate-400 hover:text-red-400 transition-colors"
                  title="Sign Out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => handleOpenAuth('login')}
                className="text-xs font-semibold px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md"
              >
                Sign In
              </button>
            )}
          </div>
        </header>
      )}

      {/* Main Views */}
      <main className="flex-1">
        {viewState === 'landing' && (
          <LandingPage
            onStartDesigning={handleStartDesigning}
            onExploreDemo={handleExploreDemo}
            onOpenAuth={handleOpenAuth}
            user={user}
            onLogout={handleLogout}
          />
        )}

        {viewState === 'requirements' && (
          <div className="min-h-[calc(100vh-60px)] p-6 flex flex-col justify-center items-center">
            <RequirementForm onGenerate={handleFormSubmit} />
          </div>
        )}

        {viewState === 'progress' && (
          <div className="min-h-[calc(100vh-60px)] p-6 flex items-center justify-center">
            <GenerationProgress onComplete={handleProgressComplete} />
          </div>
        )}

        {viewState === 'workspace' && requirements && candidateDesigns.length > 0 && (
          <DesignWorkspace
            initialRequirements={requirements}
            initialCandidateDesigns={candidateDesigns}
            onResetRequirements={() => setViewState('requirements')}
          />
        )}
      </main>
    </div>
  );
};

export default App;
