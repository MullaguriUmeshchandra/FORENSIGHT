import React, { useState, useEffect } from 'react';
import { useCase } from '../context/CaseContext';
import { gapAPI } from '../services/api';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import Modal from '../components/common/Modal';
import { AlertTriangle, Clock, RefreshCw, ChevronRight, HelpCircle, FileSearch } from 'lucide-react';

export const GapsPage = () => {
  const { currentCase } = useCase();
  const [gapData, setGapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detecting, setDetecting] = useState(false);
  const [error, setError] = useState(null);
  const [selectedGap, setSelectedGap] = useState(null);

  const fetchGaps = async () => {
    if (!currentCase) return;
    setLoading(true);
    setError(null);
    try {
      const res = await gapAPI.getGaps(currentCase.id);
      setGapData(res.data);
    } catch (err) {
      console.error('Failed to fetch gaps:', err);
      setError('Unable to load gap detection data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGaps();
  }, [currentCase]);

  const handleRunDetection = async () => {
    if (!currentCase) return;
    setDetecting(true);
    try {
      const res = await gapAPI.detectGaps(currentCase.id);
      setGapData(res.data);
    } catch (err) {
      alert('Gap detection error: ' + (err.response?.data?.detail || err.message));
    } finally {
      setDetecting(false);
    }
  };

  const gaps = gapData?.gaps || [];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Temporal Gap & Sequence Discontinuity Detection
          </h1>
          <p className="text-xs text-slate-500 font-medium mt-1">
            Mathematically evaluated time deltas between events with non-speculative explanations.
          </p>
        </div>

        <button
          onClick={handleRunDetection}
          disabled={detecting}
          className="mt-3 sm:mt-0 inline-flex items-center px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-lg shadow-sm transition-colors disabled:opacity-50 self-start"
        >
          <RefreshCw className={`w-3.5 h-3.5 mr-2 ${detecting ? 'animate-spin' : ''}`} />
          {detecting ? 'Calculating Gaps...' : 'Re-Analyze Gaps'}
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 block">Unexplained Time Gaps</span>
            <span className="text-2xl font-extrabold text-slate-900">{gapData?.unexplained_time_gaps || 0}</span>
          </div>
          <div className="p-2.5 bg-red-50 text-red-600 rounded-full">
            <Clock className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 block">Missing Expected Events</span>
            <span className="text-2xl font-extrabold text-slate-900">{gapData?.missing_expected_events || 0}</span>
          </div>
          <div className="p-2.5 bg-amber-50 text-amber-600 rounded-full">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>

        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 block">Timestamp Inconsistencies</span>
            <span className="text-2xl font-extrabold text-slate-900">{gapData?.timestamp_inconsistencies || 0}</span>
          </div>
          <div className="p-2.5 bg-blue-50 text-blue-600 rounded-full">
            <FileSearch className="w-5 h-5" />
          </div>
        </div>
      </div>

      {loading && gaps.length === 0 ? (
        <LoadingState message="Executing mathematical gap analysis..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchGaps} />
      ) : gaps.length === 0 ? (
        <EmptyState
          title="No Gaps Detected"
          description="All event sequences appear continuous or gap detection has not been executed yet."
          actionLabel="Run Gap Analysis"
          onAction={handleRunDetection}
        />
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-200 bg-slate-50/50">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Detected Time Gaps & Sequence Anomaly Registry ({gaps.length})
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-100/60 text-slate-500 font-semibold uppercase tracking-wider">
                  <th className="py-3 px-4">Gap ID</th>
                  <th className="py-3 px-4">Gap Type</th>
                  <th className="py-3 px-4">Start Time (UTC)</th>
                  <th className="py-3 px-4">End Time (UTC)</th>
                  <th className="py-3 px-4">Calculated Duration</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Forensic Explanation</th>
                  <th className="py-3 px-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {gaps.map((gap) => (
                  <tr
                    key={gap.id}
                    onClick={() => setSelectedGap(gap)}
                    className="hover:bg-slate-50 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-slate-900">GAP-{gap.id}</td>
                    <td className="py-3 px-4 font-semibold text-slate-700">{gap.gap_type.replace(/_/g, ' ')}</td>
                    <td className="py-3 px-4 font-mono text-slate-600">
                      {new Date(gap.start_time).toLocaleTimeString('en-US', { hour12: false, timeZone: 'UTC' })}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-600">
                      {new Date(gap.end_time).toLocaleTimeString('en-US', { hour12: false, timeZone: 'UTC' })}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-amber-700">
                      {gap.formatted_duration || `${Math.round(gap.duration_seconds / 60)}m`}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={gap.severity} />
                    </td>
                    <td className="py-3 px-4 text-slate-700 font-medium max-w-xs truncate" title={gap.reason}>
                      {gap.reason}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <ChevronRight className="w-4 h-4 text-slate-400 inline-block" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Gap Details Modal */}
      {selectedGap && (
        <Modal
          isOpen={Boolean(selectedGap)}
          onClose={() => setSelectedGap(null)}
          title={`Forensic Gap Inspection — GAP-${selectedGap.id}`}
        >
          <div className="space-y-4 text-xs">
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl">
              <div className="flex items-center space-x-2 text-amber-900 font-bold mb-1">
                <AlertTriangle className="w-4 h-4 shrink-0 text-amber-600" />
                <span>Forensic Finding Reason</span>
              </div>
              <p className="text-amber-950 font-medium leading-relaxed">{selectedGap.reason}</p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-[10px] font-semibold text-slate-400 block">Interval Start (UTC)</span>
                <span className="font-mono font-bold text-slate-800">{new Date(selectedGap.start_time).toUTCString()}</span>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-[10px] font-semibold text-slate-400 block">Interval End (UTC)</span>
                <span className="font-mono font-bold text-slate-800">{new Date(selectedGap.end_time).toUTCString()}</span>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-[10px] font-semibold text-slate-400 block">Unexplained Duration</span>
                <span className="font-mono font-bold text-amber-600">{selectedGap.formatted_duration || `${selectedGap.duration_seconds}s`}</span>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-[10px] font-semibold text-slate-400 block">Evaluated Severity</span>
                <div className="mt-1"><StatusBadge status={selectedGap.severity} /></div>
              </div>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Recommended Evidence Sources to Resolve Gap</span>
              <p className="text-slate-700 leading-relaxed">
                To inspect unrecorded activity during this {selectedGap.formatted_duration} window, acquire <strong>NTFS $MFT / $LogFile</strong>, <strong>Windows Prefetch files</strong>, or <strong>Network Switch Router Logs</strong>.
              </p>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default GapsPage;
