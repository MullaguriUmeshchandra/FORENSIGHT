import React, { useState, useEffect } from 'react';
import { useCase } from '../context/CaseContext';
import { recommendationAPI } from '../services/api';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import { Lightbulb, CheckCircle, RefreshCw, Shield, ArrowUpRight, Check, Clock } from 'lucide-react';

export const RecommendationsPage = () => {
  const { currentCase, initialLoaded, loadDemoCase, triggerRefresh } = useCase();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecommendations = async () => {
    if (!currentCase) {
      setRecommendations([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await recommendationAPI.getRecommendations(currentCase.id);
      setRecommendations(res.data.recommendations || []);
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
      setError('Unable to load investigative recommendations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialLoaded) {
      if (currentCase) {
        fetchRecommendations();
      } else {
        setRecommendations([]);
        setLoading(false);
      }
    }
  }, [currentCase, initialLoaded]);

  const handleGenerate = async () => {
    if (!currentCase) return;
    setGenerating(true);
    try {
      const res = await recommendationAPI.generateRecommendations(currentCase.id);
      setRecommendations(res.data.recommendations || []);
      triggerRefresh();
    } catch (err) {
      alert('Failed to generate recommendations: ' + (err.response?.data?.detail || err.message));
    } finally {
      setGenerating(false);
    }
  };

  const handleStatusChange = async (id, currentStatus) => {
    const nextStatus = currentStatus === 'PENDING' ? 'REVIEWED' : (currentStatus === 'REVIEWED' ? 'ACTIONED' : 'PENDING');
    try {
      await recommendationAPI.updateRecommendation(id, { status: nextStatus });
      fetchRecommendations();
    } catch (err) {
      console.error('Failed to update recommendation status:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Investigative Recommendations
          </h1>
          <p className="text-xs text-slate-500 font-medium mt-1">
            Defensible guidance for missing evidence acquisition derived from gap and contradiction analysis.
          </p>
        </div>

        <button
          onClick={handleGenerate}
          disabled={generating}
          className="mt-3 sm:mt-0 inline-flex items-center px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold rounded-lg shadow-sm transition-colors disabled:opacity-50 self-start"
        >
          <RefreshCw className={`w-3.5 h-3.5 mr-2 ${generating ? 'animate-spin' : ''}`} />
          {generating ? 'Formulating...' : 'Generate Recommendations'}
        </button>
      </div>

      {loading && recommendations.length === 0 ? (
        <LoadingState message="Formulating defensible recommendations..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchRecommendations} />
      ) : !currentCase ? (
        <EmptyState
          title="No Active Case Selected"
          description="Select an existing case from the top bar or load the baseline demonstration case to view recommendations."
          actionLabel="Load Demo Scenario"
          onAction={loadDemoCase}
        />
      ) : recommendations.length === 0 ? (
        <EmptyState
          title="No Recommendations Formulated"
          description="Formulate recommendations by analyzing detected timeline gaps and evidence discrepancies."
          actionLabel="Generate Recommendations"
          onAction={handleGenerate}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recommendations.map((rec) => (
            <div
              key={rec.id}
              className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <div className="p-2 bg-purple-50 text-purple-600 rounded-lg shrink-0">
                      <Lightbulb className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                      {rec.recommendation_type.replace(/_/g, ' ')}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2">
                    <StatusBadge status={rec.priority} />
                    <StatusBadge status={rec.status} />
                  </div>
                </div>

                <h3 className="text-sm font-bold text-slate-900 mb-2 leading-snug">
                  {rec.title}
                </h3>

                <p className="text-xs text-slate-600 leading-relaxed mb-4">
                  {rec.description}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] font-medium text-slate-400">
                  Confidence Score: <strong className="text-slate-800 font-mono">{Math.round(rec.confidence * 100)}%</strong>
                </span>

                <button
                  onClick={() => handleStatusChange(rec.id, rec.status)}
                  className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
                >
                  <Check className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                  Mark {rec.status === 'PENDING' ? 'Reviewed' : (rec.status === 'REVIEWED' ? 'Actioned' : 'Pending')}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RecommendationsPage;
