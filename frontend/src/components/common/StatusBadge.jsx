import React from 'react';

export const StatusBadge = ({ status, type = 'status', className = '' }) => {
  if (!status) return null;

  const statusStr = String(status).toUpperCase();

  const getStyle = () => {
    switch (statusStr) {
      // Timeline & Forensic Verification Statuses
      case 'CONFIRMED':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'INFERRED':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'MISSING':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'CONTRADICTION':
        return 'bg-orange-100 text-orange-800 border-orange-300';

      // Severities & Priorities
      case 'HIGH':
        return 'bg-red-100 text-red-700 border-red-200 font-bold';
      case 'MEDIUM':
        return 'bg-amber-100 text-amber-700 border-amber-200 font-semibold';
      case 'LOW':
        return 'bg-emerald-100 text-emerald-700 border-emerald-200';

      // Processing & Workflow Statuses
      case 'PROCESSED':
      case 'COMPLETED':
      case 'ACTIONED':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'PROCESSING':
      case 'IN_PROGRESS':
      case 'REVIEWED':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'PENDING':
      case 'OPEN':
        return 'bg-slate-100 text-slate-700 border-slate-300';
      case 'FAILED':
        return 'bg-red-50 text-red-700 border-red-200';

      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getStyle()} ${className}`}
    >
      {statusStr}
    </span>
  );
};

export default StatusBadge;
