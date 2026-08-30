import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const ErrorState = ({ message = 'Unable to load forensic data.', onRetry }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 bg-red-50/60 rounded-xl border border-red-200 text-center">
      <AlertCircle className="w-8 h-8 text-red-600 mb-2 shrink-0" />
      <h4 className="text-sm font-bold text-red-800">Connection or Processing Error</h4>
      <p className="text-xs text-red-600 mt-1 mb-4 max-w-md">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white bg-red-600 hover:bg-red-700 shadow-sm transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          Retry Request
        </button>
      )}
    </div>
  );
};

export default ErrorState;
