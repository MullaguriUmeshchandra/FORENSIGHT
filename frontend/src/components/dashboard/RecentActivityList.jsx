import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Globe, GitBranch, AlertTriangle, Lightbulb, UserCheck, ShieldAlert } from 'lucide-react';

const getActivityIcon = (action) => {
  if (action?.includes('EVIDENCE') || action?.includes('import')) return FileText;
  if (action?.includes('BROWSER')) return Globe;
  if (action?.includes('TIMELINE')) return GitBranch;
  if (action?.includes('GAP') || action?.includes('CONTRADICTION')) return AlertTriangle;
  if (action?.includes('RECOMMENDATION')) return Lightbulb;
  if (action?.includes('USER') || action?.includes('LOGIN')) return UserCheck;
  return ShieldAlert;
};

export const RecentActivityList = ({ activities = [] }) => {
  return (
    <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
      <div>
        <h3 className="text-base font-bold text-slate-800 tracking-tight mb-5">
          Recent Activity
        </h3>

        {activities.length === 0 ? (
          <p className="text-xs text-slate-400 py-6 text-center">No recent audit logs available.</p>
        ) : (
          <div className="space-y-4">
            {activities.slice(0, 5).map((act) => {
              const Icon = getActivityIcon(act.action);
              return (
                <div key={act.id} className="flex items-center justify-between py-1.5 border-b border-slate-100 last:border-0">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-50 text-blue-600 rounded-lg shrink-0">
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="text-xs font-semibold text-slate-700">
                      {act.action_label || act.action}
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-400 shrink-0">
                    {act.formatted_time || 'Just now'}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="mt-5 pt-3 border-t border-slate-100">
        <Link
          to="/investigation"
          className="text-xs font-bold text-blue-600 hover:text-blue-700 transition-colors"
        >
          View full activity log &rarr;
        </Link>
      </div>
    </div>
  );
};

export default RecentActivityList;
