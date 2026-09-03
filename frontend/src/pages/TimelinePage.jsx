import React, { useState, useEffect } from 'react';
import { useCase } from '../context/CaseContext';
import { timelineAPI, gapAPI } from '../services/api';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import Modal from '../components/common/Modal';
import { Clock, AlertTriangle, RefreshCw, Layers, ShieldCheck, ChevronRight, Info, HardDrive } from 'lucide-react';

export const TimelinePage = () => {
  const { currentCase, refreshKey, triggerRefresh } = useCase();
  const [events, setEvents] = useState([]);
  const [gaps, setGaps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [rebuilding, setRebuilding] = useState(false);
  const [error, setError] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);

  const fetchTimelineData = async () => {
    if (!currentCase) {
      setLoading(false);
      setEvents([]);
      setGaps([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [tlRes, gapRes] = await Promise.all([
        timelineAPI.getTimeline(currentCase.id),
        gapAPI.getGaps(currentCase.id)
      ]);
      setEvents(tlRes.data.events || []);
      setGaps(gapRes.data.gaps || []);
    } catch (err) {
      console.error('Failed to load timeline:', err);
      setError('Unable to load reconstructed timeline data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimelineData();
  }, [currentCase, refreshKey]);

  const handleRebuild = async () => {
    if (!currentCase) return;
    setRebuilding(true);
    try {
      await timelineAPI.rebuildTimeline(currentCase.id);
      triggerRefresh();
      await fetchTimelineData();
    } catch (err) {
      alert('Failed to rebuild timeline: ' + (err.response?.data?.detail || err.message));
    } finally {
      setRebuilding(false);
    }
  };

  // Helper to find if there is an unexplained time gap immediately preceding an event
  const getPrecedingGap = (evId) => {
    return gaps.find(g => g.next_event_id === evId && g.gap_type === 'UNEXPLAINED_TIME_GAP');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Reconstructed Chronological Timeline
          </h1>
          <p className="text-xs text-slate-500 font-medium mt-1">
            Standardized UTC event sequence derived directly from primary evidence artifacts.
          </p>
        </div>

        <button
          onClick={handleRebuild}
          disabled={rebuilding}
          className="mt-3 sm:mt-0 inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg shadow-sm transition-colors disabled:opacity-50 self-start"
        >
          <RefreshCw className={`w-3.5 h-3.5 mr-2 ${rebuilding ? 'animate-spin' : ''}`} />
          {rebuilding ? 'Correlating Timeline...' : 'Rebuild Timeline'}
        </button>
      </div>

      {loading && events.length === 0 ? (
        <LoadingState message="Reconstructing chronological timeline..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchTimelineData} />
      ) : events.length === 0 ? (
        <EmptyState
          title="Timeline Empty"
          description="No events found for this case. Upload evidence files to build the chronological timeline."
          actionLabel="Upload Evidence"
          onAction={() => window.location.href = '/evidence'}
        />
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <div className="relative border-l-2 border-slate-200 ml-4 sm:ml-32 space-y-6">
            {events.map((ev, idx) => {
              const gap = getPrecedingGap(ev.id);
              const evDate = new Date(ev.timestamp);
              const timeStr = evDate.toLocaleTimeString('en-US', { hour12: false, timeZone: 'UTC' }) + ' UTC';
              const dateStr = evDate.toLocaleDateString('en-US', { timeZone: 'UTC' });

              return (
                <React.Fragment key={ev.id}>
                  {/* Render Unexplained Time Gap Card if preceding gap exists */}
                  {gap && (
                    <div className="relative pl-6 my-6">
                      {/* Red/Amber Warning Marker */}
                      <div className="absolute -left-[17px] top-1/2 -translate-y-1/2 flex items-center justify-center w-8 h-8 rounded-full bg-amber-500 text-white font-bold text-xs ring-4 ring-white shadow-md">
                        <AlertTriangle className="w-4 h-4" />
                      </div>

                      <div className="p-4 bg-amber-50/90 border border-amber-300 rounded-xl shadow-sm">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                          <div>
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-amber-200 text-amber-900 mb-1">
                              UNEXPLAINED TIME GAP — {gap.formatted_duration || `${Math.round(gap.duration_seconds / 60)} min`}
                            </span>
                            <h4 className="text-xs font-bold text-amber-950 mt-1">
                              {gap.reason}
                            </h4>
                          </div>
                          <span className="text-[11px] font-mono font-semibold text-amber-800 mt-2 sm:mt-0">
                            {new Date(gap.start_time).toLocaleTimeString('en-US', { hour12: false, timeZone: 'UTC' })} → {new Date(gap.end_time).toLocaleTimeString('en-US', { hour12: false, timeZone: 'UTC' })} UTC
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Standard Timeline Event Node */}
                  <div
                    onClick={() => setSelectedEvent(ev)}
                    className="relative pl-6 group cursor-pointer"
                  >
                    {/* Timestamp Badge (Left of line on desktop) */}
                    <div className="hidden sm:block absolute -left-32 top-1 w-24 text-right">
                      <span className="block text-xs font-bold text-slate-800 font-mono">{timeStr}</span>
                      <span className="block text-[10px] text-slate-400 font-medium">{dateStr}</span>
                    </div>

                    {/* Timeline Node Icon Marker */}
                    <div className="absolute -left-[9px] top-1.5 w-4 h-4 rounded-full bg-white border-2 border-blue-600 group-hover:bg-blue-600 transition-colors shadow-sm" />

                    {/* Timeline Event Card */}
                    <div className="p-4 bg-slate-50/80 hover:bg-blue-50/40 border border-slate-200 hover:border-blue-300 rounded-xl shadow-sm transition-all">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div className="space-y-1">
                          <div className="sm:hidden font-mono text-xs font-bold text-blue-600">{timeStr} ({dateStr})</div>
                          <h4 className="text-xs font-bold text-slate-900 group-hover:text-blue-700 transition-colors">
                            {ev.event}
                          </h4>
                          <div className="flex items-center space-x-3 text-[11px] text-slate-500 font-medium">
                            <span className="flex items-center text-slate-600">
                              <Layers className="w-3.5 h-3.5 mr-1 text-slate-400" />
                              {ev.source}
                            </span>
                            <span>•</span>
                            <span className="flex items-center text-slate-600">
                              <HardDrive className="w-3.5 h-3.5 mr-1 text-slate-400" />
                              {ev.device}
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center space-x-2 self-start sm:self-center">
                          <StatusBadge status={ev.status} />
                          <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition-all" />
                        </div>
                      </div>
                    </div>
                  </div>
                </React.Fragment>
              );
            })}
          </div>
        </div>
      )}

      {/* Event Details Side-Panel / Modal */}
      {selectedEvent && (
        <Modal
          isOpen={Boolean(selectedEvent)}
          onClose={() => setSelectedEvent(null)}
          title="Timeline Event Details & Forensic Trace"
        >
          <div className="space-y-4 text-xs">
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Event Description</span>
              <h3 className="text-sm font-bold text-slate-900 mt-0.5">{selectedEvent.event}</h3>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-[10px] font-semibold text-slate-400 block">Timestamp (UTC)</span>
                <span className="font-mono font-bold text-slate-800">
                  {new Date(selectedEvent.timestamp).toUTCString()}
                </span>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-[10px] font-semibold text-slate-400 block">Status Verification</span>
                <div className="mt-1"><StatusBadge status={selectedEvent.status} /></div>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-[10px] font-semibold text-slate-400 block">Target Device</span>
                <span className="font-semibold text-slate-800">{selectedEvent.device}</span>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-[10px] font-semibold text-slate-400 block">Primary Source File</span>
                <span className="font-semibold text-blue-600">{selectedEvent.source}</span>
              </div>
            </div>

            <div className="p-4 bg-blue-50/70 border border-blue-200 rounded-xl">
              <div className="flex items-center space-x-2 text-blue-800 font-bold mb-1">
                <Info className="w-4 h-4 shrink-0" />
                <span>Forensic Traceability Explanation</span>
              </div>
              <p className="text-blue-900 leading-relaxed">
                This event was extracted from evidence file <code className="font-mono text-blue-800">{selectedEvent.source}</code> with confidence score <strong>{selectedEvent.confidence * 100}%</strong>. No speculative events were inserted.
              </p>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default TimelinePage;
