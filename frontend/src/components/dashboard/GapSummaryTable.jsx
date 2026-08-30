import React from 'react';
import { Link } from 'react-router-dom';
import StatusBadge from '../common/StatusBadge';

export const GapSummaryTable = ({ gapSummary = {} }) => {
  const rows = [
    {
      type: 'Unexplained Time Gaps',
      count: gapSummary['Unexplained Time Gaps'] || 0,
      status: gapSummary['Unexplained Time Gaps'] > 0 ? 'HIGH' : 'LOW'
    },
    {
      type: 'Missing Expected Events',
      count: gapSummary['Missing Expected Events'] || 0,
      status: gapSummary['Missing Expected Events'] > 0 ? 'MEDIUM' : 'LOW'
    },
    {
      type: 'Timestamp Inconsistencies',
      count: gapSummary['Timestamp Inconsistencies'] || 0,
      status: gapSummary['Timestamp Inconsistencies'] > 0 ? 'LOW' : 'LOW'
    }
  ];

  return (
    <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
      <div>
        <h3 className="text-base font-bold text-slate-800 tracking-tight mb-4">
          Gap Detection Summary
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-slate-400 font-semibold uppercase tracking-wider">
                <th className="py-2 px-1">Type</th>
                <th className="py-2 px-3 text-center">Count</th>
                <th className="py-2 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((r, i) => (
                <tr key={i} className="hover:bg-slate-50">
                  <td className="py-3 px-1 font-semibold text-slate-700">{r.type}</td>
                  <td className="py-3 px-3 text-center font-bold text-slate-900">{r.count}</td>
                  <td className="py-3 px-3 text-right">
                    <StatusBadge status={r.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-5 pt-3 border-t border-slate-100">
        <Link
          to="/gaps"
          className="text-xs font-bold text-blue-600 hover:text-blue-700 transition-colors"
        >
          View all gaps &rarr;
        </Link>
      </div>
    </div>
  );
};

export default GapSummaryTable;
