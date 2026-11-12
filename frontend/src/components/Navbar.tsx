import React from 'react';
import { FileText, Cpu, Eye, Users, PlusCircle } from 'lucide-react';
import { HealthStatus } from '../types/candidate';

interface Props {
  health: HealthStatus | null;
  onOpenHistory: () => void;
  onNewUpload: () => void;
}

export const Navbar: React.FC<Props> = ({ health, onOpenHistory, onNewUpload }) => {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={onNewUpload}>
          <div className="w-10 h-10 rounded-xl bg-brand-900 text-white flex items-center justify-center shadow-sm">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-slate-900 tracking-tight">AI Resume Parser</span>
              <span className="px-2 py-0.5 text-[10px] font-semibold bg-brand-50 text-brand-700 border border-brand-200 rounded-full">
                100% Local & Free
              </span>
            </div>
            <p className="text-xs text-slate-500">Zero Cloud APIs • High-Precision Offline Extraction</p>
          </div>
        </div>

        {/* Engine Status Indicators & Actions */}
        <div className="flex items-center gap-3">
          {/* Engine Status Badges */}
          <div className="hidden md:flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs text-slate-600">
            <div className="flex items-center gap-1.5" title="Local Ollama AI Status">
              <Cpu className="w-3.5 h-3.5 text-slate-500" />
              <span>Ollama:</span>
              <span className={`font-semibold ${health?.ollama?.available ? 'text-emerald-600' : 'text-slate-500'}`}>
                {health?.ollama?.available ? 'Active (Phi-3)' : 'Rule/NLP Mode'}
              </span>
            </div>
            <span className="text-slate-300">|</span>
            <div className="flex items-center gap-1.5" title="Tesseract OCR Status">
              <Eye className="w-3.5 h-3.5 text-slate-500" />
              <span>OCR:</span>
              <span className={`font-semibold ${health?.tesseract_ocr?.available ? 'text-emerald-600' : 'text-slate-500'}`}>
                {health?.tesseract_ocr?.available ? 'Available' : 'Native Text'}
              </span>
            </div>
          </div>

          {/* Action Buttons */}
          <button
            onClick={onOpenHistory}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition shadow-sm"
          >
            <Users className="w-4 h-4 text-slate-500" />
            <span>Saved Profiles</span>
          </button>

          <button
            onClick={onNewUpload}
            className="flex items-center gap-2 px-3.5 py-2 text-sm font-medium text-white bg-brand-900 rounded-lg hover:bg-brand-800 transition shadow-sm"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Upload Resume</span>
          </button>
        </div>
      </div>
    </header>
  );
};

