import React, { useState, useEffect } from 'react';
import { useCase } from '../context/CaseContext';
import { investigationAPI, contradictionAPI, gapAPI, timelineAPI } from '../services/api';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import Modal from '../components/common/Modal';
import KnowledgeGraph from '../components/investigation/KnowledgeGraph';
import { Network, AlertOctagon, HelpCircle, CheckCircle2, CircleDot, AlertTriangle, Layers, Info } from 'lucide-react';

export const InvestigationPage = () => {
  const { currentCase } = useCase();
  const [graphData, setGraphData] = useState(null);
  const [contradictions, setContradictions] = useState([]);
  const [gaps, setGaps] = useState([]);
  const [timelineEvents, setTimelineEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedNode, setSelectedNode] = useState(null);
  const [explainItem, setExplainItem] = useState(null);

  const fetchInvestigationData = async () => {
    if (!currentCase) {
      setLoading(false);
      setGraphData(null);
      setContradictions([]);
      setGaps([]);
      setTimelineEvents([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [gRes, cRes, gapRes, tlRes] = await Promise.all([
        investigationAPI.getRelationships(currentCase.id),
        contradictionAPI.getContradictions(currentCase.id),
        gapAPI.getGaps(currentCase.id),
        timelineAPI.getTimeline(currentCase.id)
      ]);
      setGraphData(gRes.data);
      setContradictions(cRes.data.contradictions || []);
      setGaps(gapRes.data.gaps || []);
      setTimelineEvents(tlRes.data.events || []);
    } catch (err) {
      console.error('Failed to load investigation data:', err);
      setError('Unable to load investigation relationships and telemetry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvestigationData();
  }, [currentCase]);

  const confirmedEvents = timelineEvents.filter(e => e.status === 'CONFIRMED');
  const inferredEvents = timelineEvents.filter(e => e.status === 'INFERRED');
  const missingGaps = gaps.filter(g => g.gap_type === 'MISSING_EXPECTED_EVENT');

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          Explainable Investigation & Knowledge Graph
        </h1>
        <p className="text-xs text-slate-500 font-medium mt-1">
          Interactive relationship graph, multi-source contradiction registry, and evidence explainability traces.
        </p>
      </div>

      {loading && !graphData ? (
        <LoadingState message="Building Neo4j knowledge graph relationships..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchInvestigationData} />
      ) : (
        <>
          {/* Section 1: Neo4j Relationship Knowledge Graph */}
          <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900 flex items-center">
                  <Network className="w-4 h-4 text-blue-600 mr-2" />
                  Forensic Artifact Knowledge Graph
                </h3>
                <p className="text-xs text-slate-500">
                  {graphData?.total_nodes || 0} Nodes • {graphData?.total_links || 0} Relationships (Click any node to inspect properties)
                </p>
              </div>
            </div>

            <KnowledgeGraph graphData={graphData} onSelectNode={setSelectedNode} />
          </div>

          {/* Section 2: Multi-Source Contradictions Registry */}
          <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center">
              <AlertOctagon className="w-4 h-4 text-orange-600 mr-2" />
              Detected Evidence Contradictions ({contradictions.length})
            </h3>

            {contradictions.length === 0 ? (
              <p className="text-xs text-slate-400 py-4 text-center">No cross-source evidence contradictions detected.</p>
            ) : (
              <div className="space-y-3">
                {contradictions.map((c) => (
                  <div key={c.id} className="p-4 bg-orange-50/60 border border-orange-200 rounded-xl flex items-start justify-between">
                    <div>
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="font-mono text-xs font-bold text-orange-950">CONTRA-{c.id}</span>
                        <StatusBadge status={c.contradiction_type} />
                        <StatusBadge status={c.severity} />
                      </div>
                      <p className="text-xs text-orange-950 font-medium leading-relaxed">{c.description}</p>
                    </div>

                    <button
                      onClick={() => setExplainItem({
                        title: `Contradiction CONTRA-${c.id}`,
                        source: `Artifact A #${c.artifact_a_id} vs Artifact B #${c.artifact_b_id}`,
                        confidence: c.confidence,
                        reason: c.description
                      })}
                      className="ml-4 shrink-0 inline-flex items-center px-3 py-1.5 bg-white hover:bg-orange-100 text-orange-800 border border-orange-300 rounded-lg text-xs font-bold transition-colors"
                    >
                      <HelpCircle className="w-3.5 h-3.5 mr-1" />
                      Why is this shown?
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Section 3: Confirmed vs Inferred vs Missing Evidence Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Confirmed Evidence */}
            <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center space-x-2 text-emerald-700 font-bold text-xs uppercase tracking-wider">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Confirmed Evidence ({confirmedEvents.length})</span>
              </div>
              <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                {confirmedEvents.map((ev) => (
                  <div key={ev.id} className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs flex justify-between items-center">
                    <div>
                      <span className="font-bold text-slate-800 block truncate">{ev.event}</span>
                      <span className="text-[10px] text-slate-400 font-mono">{ev.source}</span>
                    </div>
                    <button
                      onClick={() => setExplainItem({
                        title: ev.event,
                        source: ev.source,
                        evidence_id: ev.evidence_id,
                        timestamp: ev.timestamp,
                        confidence: ev.confidence,
                        reason: `Directly supported by primary evidence record from ${ev.source}.`
                      })}
                      className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                      title="Why is this shown?"
                    >
                      <HelpCircle className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Inferred Events */}
            <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center space-x-2 text-amber-700 font-bold text-xs uppercase tracking-wider">
                <CircleDot className="w-4 h-4 text-amber-600" />
                <span>Inferred Events ({inferredEvents.length})</span>
              </div>
              {inferredEvents.length === 0 ? (
                <p className="text-xs text-slate-400 py-4 text-center">No inferred events.</p>
              ) : (
                <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                  {inferredEvents.map((ev) => (
                    <div key={ev.id} className="p-2.5 bg-amber-50/60 border border-amber-200 rounded-lg text-xs flex justify-between items-center">
                      <div>
                        <span className="font-bold text-amber-950 block truncate">{ev.event}</span>
                        <span className="text-[10px] text-amber-700 font-mono">Derived Telemetry</span>
                      </div>
                      <button
                        onClick={() => setExplainItem({
                          title: ev.event,
                          source: ev.source,
                          evidence_id: ev.evidence_id,
                          timestamp: ev.timestamp,
                          confidence: ev.confidence,
                          reason: 'Derived from adjacent state changes and indirect corroborating logs.'
                        })}
                        className="p-1 text-amber-700 hover:bg-amber-100 rounded"
                      >
                        <HelpCircle className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Missing Evidence Indicators */}
            <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center space-x-2 text-red-700 font-bold text-xs uppercase tracking-wider">
                <AlertTriangle className="w-4 h-4 text-red-600" />
                <span>Missing Expected Evidence ({missingGaps.length})</span>
              </div>
              {missingGaps.length === 0 ? (
                <p className="text-xs text-slate-400 py-4 text-center">No expected evidence missing.</p>
              ) : (
                <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                  {missingGaps.map((g) => (
                    <div key={g.id} className="p-2.5 bg-red-50/80 border border-red-200 rounded-lg text-xs space-y-1">
                      <span className="font-bold text-red-900 block">MISSING EXPECTED EVENT</span>
                      <p className="text-[11px] text-red-800 leading-tight">{g.reason}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* Node Properties Panel Modal */}
      {selectedNode && (
        <Modal
          isOpen={Boolean(selectedNode)}
          onClose={() => setSelectedNode(null)}
          title={`Graph Node Properties — ${selectedNode.type}`}
        >
          <div className="space-y-3 text-xs">
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
              <span className="text-[10px] font-semibold text-slate-400 block">Node Identifier</span>
              <span className="font-mono font-bold text-blue-600">{selectedNode.id}</span>
            </div>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
              <span className="text-[10px] font-semibold text-slate-400 block">Label</span>
              <span className="font-bold text-slate-800">{selectedNode.label}</span>
            </div>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
              <span className="text-[10px] font-semibold text-slate-400 block mb-1">Properties JSON</span>
              <pre className="p-2 bg-slate-900 text-slate-200 rounded text-[11px] font-mono overflow-x-auto">
                {JSON.stringify(selectedNode.properties, null, 2)}
              </pre>
            </div>
          </div>
        </Modal>
      )}

      {/* "Why is this shown?" Explainability Modal */}
      {explainItem && (
        <Modal
          isOpen={Boolean(explainItem)}
          onClose={() => setExplainItem(null)}
          title="Why is this finding shown? (Forensic Traceability)"
        >
          <div className="space-y-4 text-xs">
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
              <div className="flex items-center space-x-2 text-blue-900 font-bold mb-1">
                <Info className="w-4 h-4 shrink-0 text-blue-600" />
                <span>Finding Title</span>
              </div>
              <h3 className="text-sm font-bold text-blue-950">{explainItem.title}</h3>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-[10px] font-semibold text-slate-400 block">Primary Source</span>
                <span className="font-semibold text-slate-800">{explainItem.source || 'N/A'}</span>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                <span className="text-[10px] font-semibold text-slate-400 block">Confidence Rating</span>
                <span className="font-bold text-blue-600">{Math.round((explainItem.confidence || 1) * 100)}%</span>
              </div>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                Forensic Trace Reason
              </span>
              <p className="text-slate-800 leading-relaxed font-medium">
                {explainItem.reason}
              </p>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default InvestigationPage;
