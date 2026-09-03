import React, { useState, useEffect } from 'react';
import { useCase } from '../context/CaseContext';
import { reportAPI } from '../services/api';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import Modal from '../components/common/Modal';
import { FileText, Download, Plus, RefreshCw, Eye, Calendar, ShieldCheck, CheckCircle } from 'lucide-react';

export const ReportsPage = () => {
  const { currentCase, triggerRefresh } = useCase();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  const [genModalOpen, setGenModalOpen] = useState(false);
  const [viewReport, setViewReport] = useState(null);
  const [reportTitle, setReportTitle] = useState('');
  const [reportFormat, setReportFormat] = useState('MARKDOWN');

  const fetchReports = async () => {
    if (!currentCase) {
      setLoading(false);
      setReports([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await reportAPI.getReports(currentCase.id);
      setReports(res.data.reports || []);
    } catch (err) {
      console.error('Failed to fetch reports:', err);
      setError('Unable to load case reports.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [currentCase]);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!currentCase) return;
    setGenerating(true);
    try {
      await reportAPI.generateReport(currentCase.id, reportTitle || `Forensic Findings Report — ${currentCase.case_number}`, reportFormat);
      setGenModalOpen(false);
      setReportTitle('');
      triggerRefresh();
      fetchReports();
    } catch (err) {
      alert('Report generation error: ' + (err.response?.data?.detail || err.message));
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async (report) => {
    const reportId = typeof report === 'object' ? report.id : report;
    const format = typeof report === 'object' ? report.report_format : 'MARKDOWN';
    const title = typeof report === 'object' ? report.title : `report_${reportId}`;

    try {
      const res = await reportAPI.downloadReport(reportId);
      const ext = format === 'JSON' ? 'json' : format === 'PDF' ? 'pdf' : 'md';
      const cleanTitle = title.toLowerCase().replace(/[^a-z0-9]/g, '_').substring(0, 40);
      const blob = new Blob([res.data]);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${cleanTitle}.${ext}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.warn('Direct blob download failed, trying authenticated link fallback:', err);
      const directUrl = reportAPI.getDownloadUrl(reportId);
      window.open(directUrl, '_blank');
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Forensic Investigation Reports
          </h1>
          <p className="text-xs text-slate-500 font-medium mt-1">
            Generate and export defensible, court-ready digital forensic timeline reconstruction reports.
          </p>
        </div>

        <button
          onClick={() => setGenModalOpen(true)}
          className="mt-3 sm:mt-0 inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg shadow-sm transition-colors self-start"
        >
          <Plus className="w-4 h-4 mr-1.5" />
          Generate New Report
        </button>
      </div>

      {loading && reports.length === 0 ? (
        <LoadingState message="Fetching forensic reports..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchReports} />
      ) : reports.length === 0 ? (
        <EmptyState
          title="No Reports Generated"
          description="Generate a comprehensive forensic report containing timeline events, calculated gaps, contradictions, and recommendations."
          actionLabel="Generate Report"
          onAction={() => setGenModalOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reports.map((rep) => (
            <div
              key={rep.id}
              className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <div className="p-2 bg-teal-50 text-teal-600 rounded-lg shrink-0">
                      <FileText className="w-5 h-5" />
                    </div>
                    <span className="font-mono text-xs font-bold text-slate-900">REP-{rep.id}</span>
                  </div>
                  <StatusBadge status={rep.report_format} />
                </div>

                <h3 className="text-sm font-bold text-slate-900 mb-2 leading-snug">
                  {rep.title}
                </h3>

                <p className="text-xs text-slate-600 leading-relaxed mb-4 line-clamp-3">
                  {rep.summary}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] font-mono text-slate-400 flex items-center">
                  <Calendar className="w-3.5 h-3.5 mr-1" />
                  {new Date(rep.created_at).toLocaleDateString('en-US')}
                </span>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setViewReport(rep)}
                    className="p-1.5 text-slate-600 hover:text-blue-600 hover:bg-slate-100 rounded-lg transition-colors"
                    title="View report"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDownload(rep)}
                    className="p-1.5 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Download report file"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Generate Report Modal */}
      {genModalOpen && (
        <Modal
          isOpen={genModalOpen}
          onClose={() => setGenModalOpen(false)}
          title="Generate Comprehensive Forensic Report"
        >
          <form onSubmit={handleGenerate} className="space-y-4 text-xs">
            <div>
              <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                Report Title
              </label>
              <input
                type="text"
                value={reportTitle}
                onChange={(e) => setReportTitle(e.target.value)}
                placeholder={`Official Case Findings — ${currentCase?.case_number}`}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-xs font-semibold text-slate-800 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>

            <div>
              <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                Output Format
              </label>
              <select
                value={reportFormat}
                onChange={(e) => setReportFormat(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-xs font-semibold text-slate-800 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none cursor-pointer"
              >
                <option value="MARKDOWN">Markdown Document (.md)</option>
                <option value="JSON">Structured JSON Findings (.json)</option>
              </select>
            </div>

            <div className="pt-2 flex justify-end space-x-2">
              <button
                type="button"
                onClick={() => setGenModalOpen(false)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={generating}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg shadow-sm disabled:opacity-50 flex items-center"
              >
                {generating ? <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : null}
                {generating ? 'Generating Report...' : 'Compile & Export Report'}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* View Report Preview Modal */}
      {viewReport && (
        <Modal
          isOpen={Boolean(viewReport)}
          onClose={() => setViewReport(null)}
          title={`Report Preview — ${viewReport.title}`}
          maxWidth="max-w-4xl"
        >
          <div className="space-y-4 text-xs font-sans">
            <div className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-xl">
              <div>
                <span className="font-bold text-slate-800 block">{viewReport.title}</span>
                <span className="text-[11px] text-slate-400 font-mono">Case ID: {viewReport.case_id}</span>
              </div>
              <button
                onClick={() => handleDownload(viewReport)}
                className="inline-flex items-center px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition-colors"
              >
                <Download className="w-3.5 h-3.5 mr-1.5" />
                Download Report File
              </button>
            </div>

            <div className="p-4 bg-slate-900 text-slate-200 rounded-xl font-mono text-[11px] max-h-96 overflow-y-auto leading-relaxed">
              <p className="font-bold text-blue-400 mb-2">SUMMARY FINDINGS:</p>
              <p className="mb-4">{viewReport.summary}</p>
              <p className="font-bold text-blue-400 mb-2">JSON METRICS:</p>
              <pre>{JSON.stringify(viewReport.findings, null, 2)}</pre>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default ReportsPage;
