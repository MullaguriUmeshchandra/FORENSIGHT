import React, { useState, useEffect } from 'react';
import { useCase } from '../context/CaseContext';
import { evidenceAPI, timelineAPI } from '../services/api';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import { Upload, FileUp, CheckCircle, AlertCircle, HardDrive, RefreshCw, Trash2, FileText } from 'lucide-react';

export const EvidencePage = () => {
  const { currentCase, triggerRefresh } = useCase();
  const [evidenceList, setEvidenceList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Form State
  const [selectedFile, setSelectedFile] = useState(null);
  const [deviceName, setDeviceName] = useState('WORKSTATION-01');
  const [sourceType, setSourceType] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const fetchEvidence = async () => {
    if (!currentCase) return;
    setLoading(true);
    setError(null);
    try {
      const res = await evidenceAPI.getEvidence(currentCase.id);
      setEvidenceList(res.data.evidence || []);
    } catch (err) {
      console.error('Failed to load evidence:', err);
      setError('Unable to load evidence inventory.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvidence();
  }, [currentCase]);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile || !currentCase) return;

    setUploading(true);
    setError(null);
    setSuccessMsg(null);

    const formData = new FormData();
    formData.append('case_id', currentCase.id);
    formData.append('device', deviceName);
    if (sourceType) formData.append('source_type', sourceType);
    formData.append('file', selectedFile);

    try {
      const res = await evidenceAPI.uploadEvidence(formData);
      setSuccessMsg(res.data.message);
      setSelectedFile(null);

      // Rebuild timeline automatically after upload
      await timelineAPI.rebuildTimeline(currentCase.id);

      // Refresh global case & dashboard state
      triggerRefresh();
      fetchEvidence();
    } catch (err) {
      console.error('Upload failed:', err);
      setError(err.response?.data?.detail || 'Failed to upload evidence file.');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Remove this evidence item and associated normalized artifacts?')) return;
    try {
      await evidenceAPI.deleteEvidence(id);
      triggerRefresh();
      fetchEvidence();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete evidence');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Evidence Collection & Ingestion
          </h1>
          <p className="text-xs text-slate-500 font-medium mt-1">
            Upload raw forensic files (CSV, JSON, LOG, TXT, XML), compute SHA-256 hashes, and normalize telemetry.
          </p>
        </div>

        <button
          onClick={fetchEvidence}
          className="mt-3 sm:mt-0 inline-flex items-center px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors self-start"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          Refresh List
        </button>
      </div>

      {/* Upload Box */}
      <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
        <h3 className="text-sm font-bold text-slate-800 tracking-tight mb-4 flex items-center">
          <Upload className="w-4 h-4 text-blue-600 mr-2" />
          Ingest New Evidence File
        </h3>

        {successMsg && (
          <div className="p-3 mb-4 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 flex items-center">
            <CheckCircle className="w-4 h-4 text-emerald-600 mr-2 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {error && (
          <div className="p-3 mb-4 bg-red-50 border border-red-200 rounded-lg text-xs text-red-800 flex items-center">
            <AlertCircle className="w-4 h-4 text-red-600 mr-2 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleUpload} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Target Device / Hostname
              </label>
              <input
                type="text"
                required
                value={deviceName}
                onChange={(e) => setDeviceName(e.target.value)}
                placeholder="WORKSTATION-01"
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-xs font-semibold text-slate-800 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Evidence Source Type (Optional)
              </label>
              <select
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-xs font-semibold text-slate-800 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none cursor-pointer"
              >
                <option value="">Auto-Detect from File Content</option>
                <option value="SYSTEM_LOGS">System Logs</option>
                <option value="BROWSER_ARTIFACTS">Browser Artifacts</option>
                <option value="FILE_METADATA">File Metadata</option>
                <option value="USB_LOGS">USB / Device Logs</option>
                <option value="NETWORK_LOGS">Network Logs</option>
                <option value="CLOUD_ACTIVITY">Cloud Activity</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
          </div>

          {/* Drag & Drop Area */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
              dragActive ? 'border-blue-500 bg-blue-50/50' : 'border-slate-300 bg-slate-50/50 hover:bg-slate-100/50'
            }`}
            onClick={() => document.getElementById('evidence-file-input').click()}
          >
            <input
              id="evidence-file-input"
              type="file"
              accept=".csv,.json,.jsonl,.ndjson,.txt,.log,.xml"
              className="hidden"
              onChange={(e) => e.target.files[0] && setSelectedFile(e.target.files[0])}
            />

            <FileUp className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            {selectedFile ? (
              <div>
                <p className="text-xs font-bold text-slate-800">{selectedFile.name}</p>
                <p className="text-[11px] text-slate-400">{(selectedFile.size / 1024).toFixed(1)} KB — Click or drag to replace</p>
              </div>
            ) : (
              <div>
                <p className="text-xs font-bold text-slate-700">Click or drag & drop forensic file here</p>
                <p className="text-[11px] text-slate-400 mt-0.5">Supports CSV, JSON, LOG, TXT, XML up to 100MB</p>
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={!selectedFile || uploading}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-lg shadow-sm transition-colors disabled:opacity-50 flex items-center justify-center"
          >
            {uploading ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> Processing & Normalizing Evidence...
              </>
            ) : (
              'Upload and Process Evidence'
            )}
          </button>
        </form>
      </div>

      {/* Evidence Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            Ingested Evidence Inventory ({evidenceList.length})
          </h3>
        </div>

        {loading && evidenceList.length === 0 ? (
          <LoadingState message="Loading evidence inventory..." />
        ) : evidenceList.length === 0 ? (
          <EmptyState
            title="No Evidence Ingested"
            description="Upload sample evidence files or run the data seed script to inspect forensic telemetry."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-100/60 text-slate-500 font-semibold uppercase tracking-wider">
                  <th className="py-3 px-4">ID</th>
                  <th className="py-3 px-4">Filename</th>
                  <th className="py-3 px-4">Source Type</th>
                  <th className="py-3 px-4">Device</th>
                  <th className="py-3 px-4">SHA-256 Hash</th>
                  <th className="py-3 px-4">Size</th>
                  <th className="py-3 px-4">Artifacts</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {evidenceList.map((ev) => (
                  <tr key={ev.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-slate-900">EV-{ev.id}</td>
                    <td className="py-3 px-4 font-semibold text-slate-800 flex items-center">
                      <FileText className="w-4 h-4 text-blue-600 mr-2 shrink-0" />
                      {ev.filename}
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-600">{ev.source_type}</td>
                    <td className="py-3 px-4 text-slate-600">{ev.device}</td>
                    <td className="py-3 px-4 font-mono text-[10px] text-slate-500" title={ev.file_hash}>
                      {ev.file_hash.substring(0, 16)}...
                    </td>
                    <td className="py-3 px-4 text-slate-600 font-mono">
                      {(ev.file_size / 1024).toFixed(1)} KB
                    </td>
                    <td className="py-3 px-4 font-bold text-blue-600">
                      {ev.artifacts_count || 0}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={ev.status} />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleDelete(ev.id)}
                        className="p-1 text-slate-400 hover:text-red-600 rounded transition-colors"
                        title="Remove evidence"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default EvidencePage;
