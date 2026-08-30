import React from 'react';
import { Inbox } from 'lucide-react';

export const EmptyState = ({ title = 'No Data Found', description = 'No records have been ingested or processed for this view yet.', actionLabel, onAction }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 bg-white rounded-xl border border-slate-200 shadow-sm text-center">
      <div className="p-3 bg-slate-100 rounded-full text-slate-400 mb-3">
        <Inbox className="w-8 h-8" />
      </div>
      <h4 className="text-sm font-bold text-slate-800">{title}</h4>
      <p className="text-xs text-slate-500 mt-1 max-w-sm leading-relaxed">{description}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="mt-4 px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition-colors"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
};

export default EmptyState;
