import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { UploadZone } from './components/UploadZone';
import { CandidateProfileView } from './components/CandidateProfileView';
import { CandidateHistoryModal } from './components/CandidateHistoryModal';
import { CandidateProfile, HealthStatus } from './types/candidate';
import { api } from './services/api';

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [activeCandidate, setActiveCandidate] = useState<CandidateProfile | null>(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const res = await api.getHealth();
      setHealth(res);
    } catch (err) {
      console.warn('Backend server may not be running yet or disconnected:', err);
    }
  };

  const handleParsingSuccess = (candidate: CandidateProfile) => {
    setActiveCandidate(candidate);
  };

  const handleNewUpload = () => {
    setActiveCandidate(null);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col selection:bg-brand-100 selection:text-brand-900">
      {/* Top Navigation */}
      <Navbar
        health={health}
        onOpenHistory={() => setIsHistoryOpen(true)}
        onNewUpload={handleNewUpload}
      />

      {/* Main Content Area */}
      <main className="flex-1 pb-16">
        {activeCandidate ? (
          <CandidateProfileView
            candidate={activeCandidate}
            onUpdateSuccess={(updated) => setActiveCandidate(updated)}
          />
        ) : (
          <UploadZone onParsingSuccess={handleParsingSuccess} />
        )}
      </main>

      {/* History Drawer Modal */}
      <CandidateHistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectCandidate={(c) => setActiveCandidate(c)}
      />

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
        <p>AI Resume Parser • 100% Free & Local Architecture • Zero External APIs</p>
      </footer>
    </div>
  );
};

export default App;

