import React from 'react';
import { ShieldCheck, AlertCircle, HelpCircle } from 'lucide-react';

interface Props {
  score?: number;
  label?: string;
  showIcon?: boolean;
}

export const ConfidenceBadge: React.FC<Props> = ({ score = 0, label, showIcon = true }) => {
  const pct = Math.round(score * 100);

  if (score >= 0.85) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
        {showIcon && <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />}
        {label ? `${label}: ` : ''}{pct}% High
      </span>
    );
  }

  if (score >= 0.60) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
        {showIcon && <AlertCircle className="w-3.5 h-3.5 text-amber-600" />}
        {label ? `${label}: ` : ''}{pct}% Medium
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
      {showIcon && <HelpCircle className="w-3.5 h-3.5 text-slate-400" />}
      {label ? `${label}: ` : ''}{pct}% Low
    </span>
  );
};

