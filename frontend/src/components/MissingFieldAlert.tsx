import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface Props {
  missingFields: string[];
}

export const MissingFieldAlert: React.FC<Props> = ({ missingFields }) => {
  if (!missingFields || missingFields.length === 0) {
    return null;
  }

  const formatFieldName = (name: string) => {
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (l) => l.toUpperCase());
  };

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6 shadow-sm">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
        <div>
          <h4 className="text-sm font-semibold text-amber-900">
            Missing Resume Information Detected ({missingFields.length} fields)
          </h4>
          <p className="text-xs text-amber-700 mt-1">
            The candidate's original resume did not contain the following fields. Per strict anti-hallucination rules, these have been preserved as <code className="bg-amber-100 px-1 py-0.5 rounded text-amber-900 font-mono">null</code>. You can manually enter them below.
          </p>
          <div className="flex flex-wrap gap-2 mt-2.5">
            {missingFields.map((field) => (
              <span
                key={field}
                className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-amber-100 text-amber-800 border border-amber-300"
              >
                Missing: {formatFieldName(field)}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

