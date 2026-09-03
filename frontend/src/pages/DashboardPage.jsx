import React, { useState, useEffect } from 'react';
import { useCase } from '../context/CaseContext';
import { dashboardAPI, investigationAPI } from '../services/api';
import MetricCard from '../components/common/MetricCard';
import InvestigationSteps from '../components/dashboard/InvestigationSteps';
import RecentActivityList from '../components/dashboard/RecentActivityList';
import GapSummaryTable from '../components/dashboard/GapSummaryTable';
import EvidenceSourceGrid from '../components/dashboard/EvidenceSourceGrid';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import CreateCaseModal from '../components/common/CreateCaseModal';
import { FolderArchive, CheckCircle, AlertTriangle, Lightbulb, FileText, FolderPlus, Shield } from 'lucide-react';

export const DashboardPage = () => {
  const { currentCase, refreshKey } = useCase();
  const [summary, setSummary] = useState(null);
  const [activities, setActivities] = useState([]);
  const [steps, setSteps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [createCaseModalOpen, setCreateCaseModalOpen] = useState(false);

  const fetchDashboardData = async () => {
    if (!currentCase) {
      setLoading(false);
      setSummary(null);
      setActivities([]);
      setSteps([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [sumRes, actRes, ovRes] = await Promise.all([
        dashboardAPI.getSummary(currentCase.id),
        dashboardAPI.getActivity(currentCase.id, 10),
        investigationAPI.getOverview(currentCase.id),
      ]);
      setSummary(sumRes.data);
      setActivities(actRes.data.activities || []);
      setSteps(ovRes.data.steps || []);
    } catch (err) {
      console.error('Dashboard data load error:', err);
      setError('Unable to load dashboard metrics from backend.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [currentCase, refreshKey]);

  if (!currentCase && !loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            AI Forensics Timeline Reconstruction
          </h1>
          <p className="text-xs text-slate-500 font-medium mt-1">
            Detect gaps, find contradictions, and discover missing evidence.
          </p>
        </div>

        <div className="p-12 text-center bg-white rounded-2xl border border-slate-200 shadow-sm max-w-xl mx-auto my-8">
          <div className="inline-flex p-4 rounded-full bg-blue-50 border border-blue-100 mb-4 text-blue-600">
            <Shield className="w-8 h-8" />
          </div>
          <h2 className="text-lg font-bold text-slate-900 mb-1">Welcome to AI Forensics Lab</h2>
          <p className="text-xs text-slate-500 max-w-md mx-auto mb-6 leading-relaxed">
            Get started by creating a new forensic case or selecting an active investigation to ingest evidence logs and reconstruct timelines.
          </p>
          <button
            onClick={() => setCreateCaseModalOpen(true)}
            className="inline-flex items-center px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-sm transition-colors"
          >
            <FolderPlus className="w-4 h-4 mr-2" />
            Create First Forensic Case
          </button>
        </div>

        <CreateCaseModal
          isOpen={createCaseModalOpen}
          onClose={() => setCreateCaseModalOpen(false)}
        />
      </div>
    );
  }

  if (loading && !summary) {
    return <LoadingState message="Connecting to forensics telemetry database..." />;
  }

  if (error && !summary) {
    return <ErrorState message={error} onRetry={fetchDashboardData} />;
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          AI Forensics Timeline Reconstruction
        </h1>
        <p className="text-xs text-slate-500 font-medium mt-1">
          Detect gaps, find contradictions, and discover missing evidence.
        </p>
      </div>

      {/* 5 Top Statistic Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Evidence Sources"
          value={summary?.evidence_sources}
          subtext={`+${summary?.evidence_sources_today || 0} added today`}
          icon={FolderArchive}
          badgeColor="blue"
          linkTo="/evidence"
        />
        <MetricCard
          title="Artifacts Processed"
          value={summary?.artifacts_processed}
          subtext="Last updated just now"
          icon={CheckCircle}
          badgeColor="green"
          linkTo="/timeline"
        />
        <MetricCard
          title="Gaps Detected"
          value={summary?.gaps_detected}
          subtext={`${summary?.unexplained_gaps_count || 0} unexplained`}
          icon={AlertTriangle}
          badgeColor="amber"
          linkTo="/gaps"
        />
        <MetricCard
          title="Recommendations"
          value={summary?.recommendations_count}
          subtext={`${summary?.high_priority_recommendations_count || 0} high priority`}
          icon={Lightbulb}
          badgeColor="purple"
          linkTo="/recommendations"
        />
        <MetricCard
          title="Reports Generated"
          value={summary?.reports_generated}
          subtext="View all reports"
          icon={FileText}
          badgeColor="teal"
          linkTo="/reports"
        />
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          <InvestigationSteps steps={steps} />
          <GapSummaryTable gapSummary={summary?.gap_summary || {}} />
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <RecentActivityList activities={activities} />
          <EvidenceSourceGrid sourceBreakdown={summary?.source_breakdown || {}} />
        </div>
      </div>

      <CreateCaseModal
        isOpen={createCaseModalOpen}
        onClose={() => setCreateCaseModalOpen(false)}
      />
    </div>
  );
};

export default DashboardPage;
