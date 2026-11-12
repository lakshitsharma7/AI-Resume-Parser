import React, { useState, useEffect } from 'react';
import { X, Search, UserCheck, Briefcase, Download, FileSpreadsheet } from 'lucide-react';
import { api } from '../services/api';
import { CandidateSummary, CandidateProfile } from '../types/candidate';
import { ConfidenceBadge } from './ConfidenceBadge';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSelectCandidate: (candidate: CandidateProfile) => void;
}

export const CandidateHistoryModal: React.FC<Props> = ({ isOpen, onClose, onSelectCandidate }) => {
  const [candidates, setCandidates] = useState<CandidateSummary[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadCandidates();
    }
  }, [isOpen]);

  const loadCandidates = async () => {
    setLoading(true);
    try {
      const data = await api.listCandidates();
      setCandidates(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (candidateId: string) => {
    try {
      const fullProfile = await api.getCandidate(candidateId);
      onSelectCandidate(fullProfile);
      onClose();
    } catch (err) {
      console.error(err);
    }
  };

  if (!isOpen) return null;

  const filtered = candidates.filter((c) => {
    const q = searchQuery.toLowerCase();
    return (
      (c.full_name && c.full_name.toLowerCase().includes(q)) ||
      (c.email && c.email.toLowerCase().includes(q)) ||
      (c.current_job_title && c.current_job_title.toLowerCase().includes(q)) ||
      (c.current_company && c.current_company.toLowerCase().includes(q))
    );
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <UserCheck className="w-5 h-5 text-brand-700" />
            <h3 className="text-lg font-bold text-slate-900">Parsed Candidate Profiles ({candidates.length})</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search */}
        <div className="p-4 border-b border-slate-100 bg-slate-50">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by name, email, job title, company..."
              className="w-full pl-9 pr-4 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>
        </div>

        {/* Candidate List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {loading ? (
            <div className="text-center py-10 text-sm text-slate-500">Loading candidate history...</div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-10 text-sm text-slate-400">No candidates match your search.</div>
          ) : (
            filtered.map((c) => (
              <div
                key={c.id}
                className="p-4 rounded-xl border border-slate-200 hover:border-brand-500 transition-all bg-white hover:bg-slate-50/50 flex items-center justify-between group"
              >
                <div className="cursor-pointer flex-1" onClick={() => handleSelect(c.id)}>
                  <div className="flex items-center gap-2">
                    <h4 className="font-bold text-slate-900 text-sm group-hover:text-brand-700 transition">
                      {c.full_name || 'Unnamed Candidate'}
                    </h4>
                    <ConfidenceBadge score={c.overall_confidence} showIcon={false} />
                  </div>
                  <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                    <span className="flex items-center gap-1">
                      <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                      {c.current_job_title || 'N/A'} {c.current_company ? `@ ${c.current_company}` : ''}
                    </span>
                    <span>•</span>
                    <span>{c.total_experience_years} yrs exp</span>
                    {c.email && (
                      <>
                        <span>•</span>
                        <span>{c.email}</span>
                      </>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2 pl-4">
                  <button
                    onClick={() => api.downloadJson(c.id, c.full_name || 'Candidate')}
                    className="p-2 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition"
                    title="Export JSON"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => api.downloadExcel(c.id, c.full_name || 'Candidate')}
                    className="p-2 text-slate-400 hover:text-emerald-600 rounded-lg hover:bg-slate-100 transition"
                    title="Export Excel"
                  >
                    <FileSpreadsheet className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
