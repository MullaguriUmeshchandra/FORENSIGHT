import React from 'react';
import { CheckCircle2, Circle, Clock, AlertCircle, FolderPlus, Database, GitCommit, AlertTriangle, FileText } from 'lucide-react';

const STEP_ICONS = [
  FolderPlus,
  Database,
  GitCommit,
  AlertTriangle,
  FileText
];

export const InvestigationSteps = ({ steps = [] }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />;
      case 'in_progress':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin shrink-0" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />;
      default:
        return <Circle className="w-5 h-5 text-slate-300 shrink-0" />;
    }
  };

  return (
    <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
      <h3 className="text-base font-bold text-slate-800 tracking-tight mb-5">
        Investigation Overview
      </h3>

      <div className="space-y-4">
        {steps.map((step, idx) => {
          const StepIcon = STEP_ICONS[idx] || FolderPlus;
          return (
            <div key={step.step_number || idx} className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 transition-colors">
              <div className="flex items-center space-x-3.5">
                <div className="flex items-center justify-center w-7 h-7 rounded-full bg-blue-600 text-white font-bold text-xs shrink-0">
                  {step.step_number}
                </div>
                <div className="p-2 bg-slate-100 rounded-lg text-slate-600 shrink-0 hidden sm:block">
                  <StepIcon className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-800">{step.title}</h4>
                  <p className="text-[11px] text-slate-500 leading-tight">{step.description}</p>
                </div>
              </div>
              <div>{getStatusIcon(step.status)}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default InvestigationSteps;
