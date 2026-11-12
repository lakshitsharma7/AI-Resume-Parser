import React, { useState, useRef } from 'react';
import { UploadCloud, CheckCircle2, AlertCircle, Loader2, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import { CandidateProfile } from '../types/candidate';

interface Props {
  onParsingSuccess: (candidate: CandidateProfile) => void;
}

export const UploadZone: React.FC<Props> = ({ onParsingSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [progressStep, setProgressStep] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = async (file: File) => {
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    const allowed = ['.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg'];

    if (!allowed.includes(ext)) {
      setErrorMsg(`Unsupported file type '${ext}'. Please upload a PDF, DOCX, or scanned image.`);
      return;
    }

    if (file.size > 25 * 1024 * 1024) {
      setErrorMsg('File exceeds 25 MB size limit.');
      return;
    }

    setErrorMsg(null);
    setIsLoading(true);

    try {
      setProgressStep('Reading document and analyzing page columns...');
      await new Promise((r) => setTimeout(r, 600));

      setProgressStep('Extracting candidate profile with AI & NLP engine...');
      const response = await api.uploadResume(file);

      setProgressStep('Validating schema and computing non-overlapping experience...');
      await new Promise((r) => setTimeout(r, 400));

      if (response && response.candidate) {
        onParsingSuccess(response.candidate);
      } else {
        throw new Error('Failed to retrieve structured candidate profile.');
      }
    } catch (err: any) {
      console.error(err);
      const detail = err.response?.data?.detail || err.message || 'Error parsing resume file.';
      setErrorMsg(detail);
    } finally {
      setIsLoading(false);
      setProgressStep('');
    }
  };

  return (
    <div className="max-w-3xl mx-auto my-8 px-4">
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-brand-50 text-brand-700 rounded-full text-xs font-semibold mb-3 border border-brand-200">
          <Sparkles className="w-3.5 h-3.5 text-brand-600" />
          <span>Automated Candidate Data Extraction</span>
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight sm:text-4xl">
          Upload Resume. Extract Instantly.
        </h1>
        <p className="mt-2 text-sm text-slate-600 max-w-xl mx-auto">
          Drag and drop any candidate resume in PDF or Word format. The engine will extract full contact info, work history, categorized skills, education, and calculate overlap-free experience.
        </p>
      </div>

      {errorMsg && (
        <div className="mb-6 p-4 bg-rose-50 border border-rose-200 rounded-xl flex items-start gap-3 text-rose-800 text-sm">
          <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold">Extraction Error:</span> {errorMsg}
          </div>
        </div>
      )}

      {/* Dropzone Card */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isLoading && fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-2xl p-10 text-center transition-all cursor-pointer ${
          isDragging
            ? 'border-brand-600 bg-brand-50/50 scale-[1.01]'
            : 'border-slate-300 hover:border-brand-500 bg-white hover:bg-slate-50/50'
        } ${isLoading ? 'pointer-events-none opacity-80' : 'shadow-sm'}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.doc,.png,.jpg,.jpeg"
          onChange={handleFileSelect}
          className="hidden"
        />

        {isLoading ? (
          <div className="py-8 flex flex-col items-center justify-center">
            <Loader2 className="w-12 h-12 text-brand-700 animate-spin mb-4" />
            <h3 className="text-lg font-semibold text-slate-900">Processing Resume...</h3>
            <p className="text-sm text-slate-500 mt-2 font-medium">{progressStep}</p>
            <div className="w-64 bg-slate-200 rounded-full h-2 mt-4 overflow-hidden">
              <div className="bg-brand-700 h-2 rounded-full animate-pulse w-3/4"></div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <div className="w-16 h-16 rounded-2xl bg-brand-50 text-brand-700 flex items-center justify-center mb-4">
              <UploadCloud className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">
              Drag & drop your resume here, or <span className="text-brand-700 underline">browse files</span>
            </h3>
            <p className="text-xs text-slate-500 mt-2">
              Supports PDF, DOCX, Scanned PDFs, and image resumes (up to 25 MB)
            </p>

            <div className="flex items-center gap-6 mt-6 text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Multi-column layouts
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Overlap-free dates
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Zero cloud calls
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
