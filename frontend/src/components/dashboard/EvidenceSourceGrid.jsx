import React from 'react';
import { Link } from 'react-router-dom';
import { Monitor, Globe, FileText, Usb, Network, Cloud } from 'lucide-react';

const SOURCES = [
  { key: 'System Logs', icon: Monitor, label: 'System Logs', type: 'SYSTEM_LOGS' },
  { key: 'Browser Artifacts', icon: Globe, label: 'Browser Artifacts', type: 'BROWSER_ARTIFACTS' },
  { key: 'File Metadata', icon: FileText, label: 'File Metadata', type: 'FILE_METADATA' },
  { key: 'USB / Device Logs', icon: Usb, label: 'USB / Device Logs', type: 'USB_LOGS' },
  { key: 'Network Logs', icon: Network, label: 'Network Logs', type: 'NETWORK_LOGS' },
  { key: 'Cloud Activity', icon: Cloud, label: 'Cloud Activity', type: 'CLOUD_ACTIVITY' },
];

export const EvidenceSourceGrid = ({ sourceBreakdown = {} }) => {
  return (
    <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
      <div>
        <h3 className="text-base font-bold text-slate-800 tracking-tight mb-4">
          Evidence Sources
        </h3>

        <div className="grid grid-cols-3 gap-3">
          {SOURCES.map((src) => {
            const Icon = src.icon;
            const count = sourceBreakdown[src.key] || 0;
            return (
              <Link
                key={src.key}
                to={`/evidence?type=${src.type}`}
                className="flex flex-col items-center justify-center p-3 rounded-xl border border-slate-100 bg-slate-50/60 hover:bg-blue-50/60 hover:border-blue-200 transition-all text-center group"
              >
                <div className="p-2.5 rounded-full bg-white text-slate-600 group-hover:text-blue-600 group-hover:shadow-sm border border-slate-200 mb-2 transition-all">
                  <Icon className="w-5 h-5" />
                </div>
                <span className="text-[11px] font-bold text-slate-700 leading-tight block mb-0.5">
                  {src.label}
                </span>
                <span className="text-[10px] font-semibold text-slate-400">
                  {count} file{count === 1 ? '' : 's'}
                </span>
              </Link>
            );
          })}
        </div>
      </div>

      <div className="mt-5 pt-3 border-t border-slate-100">
        <Link
          to="/evidence"
          className="text-xs font-bold text-blue-600 hover:text-blue-700 transition-colors"
        >
          Manage sources &rarr;
        </Link>
      </div>
    </div>
  );
};

export default EvidenceSourceGrid;
